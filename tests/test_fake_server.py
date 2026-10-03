# fake server one-shot faults
import unittest

from helpers import fake_server

ONE_SHOT_FAULTS = ("http401_once", "error_in_200:Item.list")


def _log_in(server):
    _, reply = server.request("POST", "/api/auth/login")
    return reply["token"]


def _send_rpc(server, token, method, params=None):
    # returns (http status, reply)
    body = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}
    return server.request("POST", "/api/mcp", token,body)


class OneShotFaultTests(unittest.TestCase):  # FAKE-1

    def test_faults_fire_once(self):
        # 401 only hits the first tools/list and injected error only the first Item.list
        server = fake_server(ONE_SHOT_FAULTS)
        token = _log_in(server)

        first_status, _ = _send_rpc(server, token, "tools/list")
        second_status, _ = _send_rpc(server, token, "tools/list")
        self.assertEqual(first_status, 401)
        self.assertEqual(second_status, 200)

        item_list_call = {"name": "Item.list", "arguments": {}}
        status, first_reply = _send_rpc(server, token, "tools/call", item_list_call)
        self.assertEqual(status, 200)
        self.assertEqual(first_reply["error"]["data"]["code"], "agent_error")
        self.assertEqual(first_reply["error"]["message"], "Injected failure (fake server)")

        _, second_reply = _send_rpc(server, token, "tools/call", item_list_call)
        self.assertIn("result", second_reply)
        self.assertNotIn("error", second_reply)

    def test_disarmed_no_fault(self):
        # armed off before first call so tools/list just gives 200 straight away
        server = fake_server(ONE_SHOT_FAULTS)
        server.armed = False
        token = _log_in(server)

        status, _ = _send_rpc(server, token, "tools/list")

        self.assertEqual(status, 200)


if __name__ == "__main__":
    unittest.main()