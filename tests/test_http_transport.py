# STRIDE S5 - https only and a redirect is never followed
# urllib's default opener re-sent the Authorization header to any host a 3xx named (even plain http) and took that hosts reply as the platform's
import json
import threading
import unittest
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from agent.http import NO_REDIRECT_OPENER, HttpTransport

DUMMY_TOKEN = "hunter2-token"  # fake, only goes to the local stand-in servers
REDIRECT_PATH = "/collect"  # where the first one redirects to
TIMEOUT = 5  # socket timeout per request
POLL = 0.01  # shutdown poll, keeps tests fast


class _Handler(BaseHTTPRequestHandler):
    # answers for a FakeHost and keeps test output quiet

    def log_message(self, *args):
        pass

    def _answer(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length:
            self.rfile.read(length)
        self.server.received.append((self.command, self.path, self.headers.get("Authorization")))
        if self.server.redirect_to:
            self.send_response(302)
            self.send_header("Location", self.server.redirect_to + REDIRECT_PATH)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        body = json.dumps({"origin": "the other host, not the platform"}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    do_GET = _answer
    do_POST = _answer


class FakeHost(ThreadingHTTPServer):
    # one web host on 127.0.0.1, notes every request then answers 302 (if redirect_to set) or 200

    def __init__(self, redirect_to=None):
        super().__init__(("127.0.0.1", 0), _Handler)
        self.redirect_to = redirect_to
        self.received = []  # (method, path, auth header or None)

    @property
    def url(self):
        return f"http://127.0.0.1:{self.server_address[1]}"


class HttpsOnlyTests(unittest.TestCase):

    def test_non_https_refused(self):
        # not https (http, ftp, no scheme at all) -> ValueError
        for base_url in ("http://platform.example.test", "ftp://platform.example.test", "platform.example.test"):
            with self.subTest(base_url=base_url):
                with self.assertRaises(ValueError) as refused:
                    HttpTransport(base_url)
                self.assertEqual(str(refused.exception), f"base_url must start with https:// (got {base_url!r})")


class RedirectRefusalTests(unittest.TestCase):

    def _start(self, origin):
        # serve origin on a daemon thread till the test ends
        threading.Thread(target=origin.serve_forever, kwargs={"poll_interval": POLL}, daemon=True).start()
        self.addCleanup(origin.server_close)
        self.addCleanup(origin.shutdown)
        return origin

    def setUp(self):
        # 2 hosts, the fake platform 302s to the other one
        self.other_host = self._start(FakeHost())
        self.platform = self._start(FakeHost(redirect_to=self.other_host.url))

    def test_opener_doesnt_follow(self):
        # shared opener gives the 302 back as an error so the other host never sees a request or the token
        request = urllib.request.Request(self.platform.url + "/api/mcp", b"{}", method="POST", headers={"Authorization": f"Bearer {DUMMY_TOKEN}"})
        with self.assertRaises(urllib.error.HTTPError) as refused:
            NO_REDIRECT_OPENER.open(request, timeout=TIMEOUT)
        self.addCleanup(refused.exception.close)
        self.assertEqual(refused.exception.code, 302)
        self.assertEqual(refused.exception.headers["Location"], self.other_host.url + REDIRECT_PATH)
        self.assertEqual(self.platform.received, [("POST", "/api/mcp", f"Bearer {DUMMY_TOKEN}")])
        self.assertEqual(self.other_host.received, [])

    def test_transport_302_once(self):
        # HttpTransport returns the 302 as its status, tries once, token never reaches the other host
        transport = HttpTransport("https://platform.example.test", retries=3)
        transport.base_url = self.platform.url  # stand-in is plain http, https check only runs in __init__
        # http.py never closes the 302 HTTPError so you might see a ResourceWarning, test is still fine
        status, data = transport.request("POST", "/api/mcp", token=DUMMY_TOKEN, body={})
        self.assertEqual((status, data), (302, ""))
        self.assertEqual(self.platform.received, [("POST", "/api/mcp", f"Bearer {DUMMY_TOKEN}")])
        self.assertEqual(self.other_host.received, [])


if __name__ == "__main__":
    unittest.main()
