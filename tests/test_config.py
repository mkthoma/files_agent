# settings tests: .env parsing and the live write switch
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from agent.config import get_settings, load_env
from agent.runtime import WritesNotAllowed, check_write_permission

from helpers import quiet_settings

# temp .env contents for CONFIG-1
ENV_FILE_LINES = ["# c", "AS_EMAIL='file@x'", "AS_MAX_TURNS = 7", "BAD LINE", 'AS_MODEL="m1"', "OTHER=1"]


def _shell_without_agent_settings(**extra):
    # os.environ minus all AS_* / ANTHROPIC_* vars, plus extra
    kept = {key: value for key, value in os.environ.items() if not key.startswith(("AS_","ANTHROPIC_"))}
    return {**kept, **extra}


def _env_file_with_writes_on():
    # fake load_env, like the .env file has AS_ALLOW_WRITES=1
    return {"AS_ALLOW_WRITES": "1"}


class EnvFileTests(unittest.TestCase):  # CONFIG-1

    def test_env_file_parse(self):
        # 4 keys kept, quotes stripped, comment and bad line skipped. shell AS_MODEL wins over the file
        env_file = Path(self.enterContext(tempfile.TemporaryDirectory())) / ".env"
        env_file.write_text("\n".join(ENV_FILE_LINES), encoding="utf-8")

        # clear AS_* first so someones own shell settings cant change the result
        with mock.patch.dict(os.environ, _shell_without_agent_settings(AS_MODEL="from-env"), clear=True):
            values = load_env(env_file)

        self.assertEqual(values, {"AS_EMAIL": "file@x", "AS_MAX_TURNS": "7", "AS_MODEL": "from-env", "OTHER": "1"})


class WritePermissionTests(unittest.TestCase):  # CONFIG-2

    def test_allowed_cases(self):
        # fake apply, live plan and live apply with AS_ALLOW_WRITES=1 are all allowed
        self.assertIsNone(check_write_permission("fake", "apply", quiet_settings()))
        self.assertIsNone(check_write_permission("live", "plan", quiet_settings()))
        self.assertIsNone(check_write_permission("live", "apply", quiet_settings(AS_ALLOW_WRITES="1")))

    def test_live_write_refused(self):
        # live apply refused without AS_ALLOW_WRITES, and on suryodaya even with it
        with self.assertRaises(WritesNotAllowed) as no_switch:
            check_write_permission("live", "apply", quiet_settings())
        self.assertIn("AS_ALLOW_WRITES", str(no_switch.exception))

        suryodaya = get_settings("suryodaya", env={"AS_ALLOW_WRITES": "1"})
        with self.assertRaises(WritesNotAllowed) as wrong_business:
            check_write_permission("live", "apply", suryodaya)
        self.assertEqual(str(wrong_business.exception), "Live writes are only allowed on keystone.")

    def test_env_file_cant_turn_on_writes(self):
        # AS_ALLOW_WRITES=1 from .env should be ignored, only the shell can turn writes on
        with mock.patch("agent.config.load_env", _env_file_with_writes_on):
            with mock.patch.dict(os.environ, _shell_without_agent_settings(), clear=True):
                settings = get_settings("keystone")

        self.assertFalse(settings.allow_writes)


if __name__ == "__main__":
    unittest.main()