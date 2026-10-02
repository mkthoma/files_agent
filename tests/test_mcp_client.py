import unittest

from agent.auth import Session
from agent.mcp_client import McpClient, McpError
from agent.redact import Redactor
from agent.trace import Trace


class StubSession:
    def __init__(self, replies):
        self.replies = list(replies)
        self.flags = []

    def request(self, method, path, body=None, idempotent=True):
        self.flags.append(idempotent)
        return self.replies.pop(0)


def client_with(replies):
    return McpClient(StubSession(replies), Trace(None, Redactor())), None


def good_reply():
    return (200, {"result": {"content": [{"type": "text", "text": "{}"}]}})


class McpClientTest(unittest.TestCase):
    def test_error_inside_200_raises(self):
        client, _ = client_with([(200, {"jsonrpc": "2.0", "id": 1,
                                        "error": {"code": -32000, "message": "boom", "data": {"code": "x"}}})])
        with self.assertRaises(McpError) as ctx:
            client.call("FileAttachment.list", {})
        self.assertEqual(ctx.exception.code, -32000)
        self.assertEqual(ctx.exception.data_code, "x")

    def test_plain_string_error_raises(self):
        client, _ = client_with([(200, {"error": "plain string"})])
        with self.assertRaises(McpError):
            client.call("FileAttachment.list", {})

    def test_http_500_raises(self):
        client, _ = client_with([(500, {})])
        with self.assertRaises(McpError) as ctx:
            client.call("FileAttachment.list", {})
        self.assertEqual(ctx.exception.code, 500)

    def test_non_json_reply_raises(self):
        client, _ = client_with([(200, "<html>")])
        with self.assertRaises(McpError):
            client.call("FileAttachment.list", {})

    def test_is_error_raises(self):
        reply = (200, {"result": {"isError": True, "content": [{"type": "text", "text": '{"m": 1}'}]}})
        client, _ = client_with([reply])
        with self.assertRaises(McpError) as ctx:
            client.call("FileAttachment.list", {})
        self.assertEqual(ctx.exception.data_code, "is_error")

    def test_writes_are_not_idempotent(self):
        stub = StubSession([good_reply(), good_reply()])
        client = McpClient(stub, Trace(None, Redactor()))
        client.call("AgentEscalation.create", {})
        client.call("FileAttachment.list", {})
        self.assertEqual(stub.flags, [False, True])


class StubTransport:
    def __init__(self, replies):
        self.replies = list(replies)
        self.logins = 0

    def request(self, method, path, token=None, body=None, idempotent=True):
        if path == "/api/auth/login":
            self.logins += 1
            return 200, {"token": f"tok-{self.logins}-abcdef"}
        return self.replies.pop(0)


class LoginTest(unittest.TestCase):
    def test_401_logs_in_again_once(self):
        transport = StubTransport([(401, {}), (200, {"ok": True})])
        trace = Trace(None, Redactor())
        session = Session(transport, "a@b.c", "s3cret-pass", trace)
        status, _ = session.request("GET", "/api/x")
        self.assertEqual(status, 200)
        self.assertEqual(transport.logins, 2)
        self.assertEqual(len(trace.of_kind("relogin")), 1)

    def test_second_401_is_returned_not_retried_forever(self):
        transport = StubTransport([(401, {}), (401, {})])
        trace = Trace(None, Redactor())
        session = Session(transport, "a@b.c", "s3cret-pass", trace)
        status, _ = session.request("GET", "/api/x")
        self.assertEqual(status, 401)
        self.assertEqual(transport.logins, 2)
        self.assertEqual(len(trace.of_kind("relogin")), 1)


if __name__ == "__main__":
    unittest.main()
