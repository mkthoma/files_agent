# STRIDE I4 + I11 - secrets stay out of reprs, tracebacks, traces and the repo
# all values are dummies (none shaped like a real key). scan canary gets built at run time so this file never has the string the scan looks for
import json
import os
import subprocess
import sys
import tempfile
import traceback
import unittest
import uuid
from pathlib import Path
from unittest import mock
from urllib.parse import quote, quote_plus
from agent.config import get_settings, load_env
from agent.redact import Redactor
from helpers import REPO_ROOT, build_runtime, new_set_name, offline_env, quiet_settings, remove_run_set

DUMMY_PASSWORD = "dummy-seat-pass-4471"  # fake keystone password
DUMMY_MODEL_KEY = "dummy-model-key-0001"  # fake model key, on purpose not shaped like one
DUMMY_SECRETS = {"AS_KEYSTONE_PASSWORD": DUMMY_PASSWORD, "ANTHROPIC_API_KEY": DUMMY_MODEL_KEY}
MASKED = "'[REDACTED]'"  # repr() of a Secret
# neither dummy, and neither field by name. 2 layers keep a secret out of a repr: fields left out (config.py)
# + each value is a Secret with a masked repr (redact.py). field names catch losing layer 1, the Secret would hide that
LEAK_MARKERS = (DUMMY_PASSWORD, DUMMY_MODEL_KEY, "password=", "anthropic_api_key=")

WEIRD_SECRET = 'dummy"päss/word 1&x'  # quote, non ascii letter, slash, space and & all get escaped

CANARY_HEAD = "i11-scan-canary-"  # + a random tail, only joined at run time
PLANTED_LINE = 2  # line 2 of 3
SCAN_RULE = "a value from .env (or --also)"  # rule name secret_scan.py gives an --also hit
SCAN_TIMEOUT = 300  # secs, scan reads every tracked file + all of runs/


def _clean_env():
    # os.environ minus AS_* / ANTHROPIC_* so a real secret in the shell cant get read
    return {key: value for key, value in os.environ.items() if not key.startswith(("AS_", "ANTHROPIC_"))}


def _leaks(text):
    # LEAK_MARKERS found in text - short list so a failure doesnt dump a 270kB repr
    return [marker for marker in LEAK_MARKERS if marker in text]


def _make_env(folder, values):
    # .env with these values, owner only so load_env doesnt print its shared file warning on posix
    env_file = Path(folder) / ".env"
    env_file.write_text("".join(f"{key}={value}\n" for key, value in values.items()), encoding="utf-8")
    env_file.chmod(0o600)
    return env_file


class SecretReprTests(unittest.TestCase):  # I4

    def test_settings_repr(self):
        # repr of settings has neither dummy and leaves both fields out
        settings = quiet_settings(**DUMMY_SECRETS)
        shown = repr(settings)
        # values still there for login/model, only repr hides them
        self.assertEqual(settings.password, DUMMY_PASSWORD)
        self.assertEqual(settings.anthropic_api_key, DUMMY_MODEL_KEY)
        self.assertEqual(_leaks(shown), [])

    def test_runtime_repr(self):
        # repr of a whole runtime (what print(rt) or a test diff shows) has neither
        rt, _ = build_runtime("plan", settings=quiet_settings(**DUMMY_SECRETS))
        shown = repr(rt)
        self.assertEqual(rt.settings.password, DUMMY_PASSWORD)  # really logged in with the dummy
        self.assertEqual(_leaks(shown), [])

    def test_traceback_locals(self):
        # .env with dummies + AS_MAX_USD=nan fails, traceback printed with locals shows neither
        # helper writes it so this frames locals (printed below too) only hold load_env's masked values
        env_file = _make_env(self.enterContext(tempfile.TemporaryDirectory()), {**DUMMY_SECRETS, "AS_MAX_USD": "nan"})
        with mock.patch.dict(os.environ, _clean_env(), clear=True):
            values = load_env(env_file)
        # not assertRaises - it strips the frames and the locals are the whole point here
        try:
            get_settings("keystone", env=values)
        except ValueError as err:
            # what unittest --locals / pytest -l would print
            printed = "".join(traceback.TracebackException.from_exception(err, capture_locals=True).format())
        else:
            self.fail("get_settings accepted AS_MAX_USD=nan")
        self.assertNotIn(DUMMY_PASSWORD, printed)
        self.assertNotIn(DUMMY_MODEL_KEY, printed)
        self.assertIn("AS_MAX_USD must be a finite number", printed)  # right traceback
        self.assertIn(MASKED, printed)  # .env values are in the locals, masked


class EncodedSecretTests(unittest.TestCase):  # I4

    def test_json_escaped_masked(self):
        # echoed json body has the secret with its quote (and maybe accented letter) escaped, both forms get masked
        redact = Redactor([WEIRD_SECRET])
        ascii_body = json.dumps({"echo": WEIRD_SECRET})  # quote turns into \" and ä into \u00e4
        utf8_body = json.dumps({"echo": WEIRD_SECRET}, ensure_ascii=False)  # quote escaped, ä stays
        self.assertNotIn(WEIRD_SECRET, ascii_body)  # so its not just the plain secret getting masked
        self.assertEqual(redact(ascii_body), '{"echo": "[REDACTED]"}')
        self.assertEqual(redact(utf8_body), '{"echo": "[REDACTED]"}')

    def test_url_encoded_masked(self):
        # percent encoded in a query string, space as %20 or +
        redact = Redactor([WEIRD_SECRET])
        query = "https://example.test/login?pw=" + quote(WEIRD_SECRET, safe="")  # space as %20
        form = "pw=" + quote_plus(WEIRD_SECRET)  # space as +
        self.assertEqual(redact(query), "https://example.test/login?pw=[REDACTED]")
        self.assertEqual(redact(form), "pw=[REDACTED]")


class SecretScanTests(unittest.TestCase):  # I11

    def test_scan_finds_canary(self):
        # canary planted in a scratch file under runs/ is found, reported as file:line, never printed
        canary = CANARY_HEAD + uuid.uuid4().hex
        scratch = new_set_name("i11-scan")
        self.addCleanup(remove_run_set, scratch)  # register first so the folder goes even if something below fails
        planted = REPO_ROOT / "runs" / scratch / "planted.txt"
        planted.parent.mkdir()
        planted.write_text(f"first line\nnote: {canary}\nlast line\n", encoding="utf-8")
        # the documented command. offline_env blanks the real passwords/key so only the canary gets searched
        scan = subprocess.run([sys.executable, "scripts/secret_scan.py", "--also", canary], cwd=REPO_ROOT, env=offline_env(), capture_output=True, text=True, encoding="utf-8", timeout=SCAN_TIMEOUT)
        ours = [line for line in scan.stdout.splitlines() if scratch in line]
        self.assertEqual(ours, [f"runs/{scratch}/planted.txt:{PLANTED_LINE}: {SCAN_RULE}"])
        self.assertEqual(scan.returncode, 1)
        self.assertNotIn(canary, scan.stdout)
        self.assertNotIn(canary, scan.stderr)


if __name__ == "__main__":
    unittest.main()
