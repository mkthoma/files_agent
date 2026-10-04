# STRIDE T14 - a task file cant take over, rename or escape another task, or sneak in a wrong type
# all task files here go in a temp folder, the real harness/tasks/ isnt used
import tempfile
import unittest
from pathlib import Path
from harness.tasks import load_all, load_task

QUESTION = "Tidy the incoming folder."  # same question as TI1
ID_RULE = "id must equal the file name {stem!r} and use only letters, digits, '_' and '-'; found {found!r}"
ESCAPE_ID = "../../escape"  # as a run folder this climbs out of the run set


def _write_task(folder, file_name, body):
    path = folder / file_name
    path.write_text(body, encoding="utf-8")
    return path

class CaseSensitiveFolder:
    # fake task folder on a case sensitive fs (linux) where TI1.toml and ti1.toml can sit side by side.
    # windows folds case so one real folder cant hold both here. load_all only calls glob()
    def __init__(self, paths):
        self.paths = paths

    def glob(self, pattern):
        return list(self.paths)


class TaskIdTests(unittest.TestCase):

    def setUp(self):
        self.folder = Path(self.enterContext(tempfile.TemporaryDirectory()))

    def test_id_must_match_filename(self):
        # B.toml with id = "A" is refused and the error names B.toml
        path = _write_task(self.folder, "B.toml", f'id = "A"\nquestion = "{QUESTION}"\n')
        with self.assertRaises(ValueError) as caught:
            load_task(path)
        self.assertEqual(str(caught.exception), "B.toml: " + ID_RULE.format(stem="B", found="A"))

    def test_dot_dot_id_refused(self):
        # '../../escape' would put the run files outside the run set
        path = _write_task(self.folder, "escape.toml", f'id = "{ESCAPE_ID}"\nquestion = "{QUESTION}"\n')
        with self.assertRaises(ValueError) as caught:
            load_task(path)
        self.assertEqual(str(caught.exception), "escape.toml: " + ID_RULE.format(stem="escape", found=ESCAPE_ID))

    def test_duplicate_id_refused(self):
        # new TI1b.toml saying id = "TI1" with no expectations fails the whole folder, naming TI1b.toml
        _write_task(self.folder, "TI1.toml", f'id = "TI1"\nquestion = "{QUESTION}"\n')
        _write_task(self.folder, "TI1b.toml", f'id = "TI1"\nquestion = "{QUESTION}"\n\n[expect]\n')
        with self.assertRaises(ValueError) as caught:
            load_all(self.folder)
        self.assertEqual(str(caught.exception), "TI1b.toml: " + ID_RULE.format(stem="TI1b", found="TI1"))

    def test_case_only_ids_refused(self):
        # TI1.toml + ti1.toml would share one run folder on windows, 2nd one refused naming both
        # each file in its own sub folder ("1" sorts before "2" everywhere) so TI1.toml is always read first
        for sub_folder in ("1", "2"):
            (self.folder / sub_folder).mkdir()
        upper = _write_task(self.folder / "1", "TI1.toml", f'id = "TI1"\nquestion = "{QUESTION}"\n')
        lower = _write_task(self.folder / "2", "ti1.toml", f'id = "ti1"\nquestion = "{QUESTION}"\n')
        with self.assertRaises(ValueError) as caught:
            load_all(CaseSensitiveFolder([upper, lower]))
        self.assertEqual(str(caught.exception), "task id 'ti1' in ti1.toml is already used by TI1.toml")


class TaskFieldTypeTests(unittest.TestCase):

    def setUp(self):
        self.folder = Path(self.enterContext(tempfile.TemporaryDirectory()))

    def test_quoted_live_write(self):
        # live_write = "false" is a non empty string so it would count as true
        path = _write_task(self.folder, "X1.toml", f'id = "X1"\nquestion = "{QUESTION}"\nmode = "apply"\nlive_write = "false"\n')
        with self.assertRaises(ValueError) as caught:
            load_task(path)
        self.assertEqual(str(caught.exception), "X1.toml: live_write must be true or false")

    def test_zero_passes(self):
        # passes = 0 asks the agent nothing but still gets scored
        path = _write_task(self.folder, "X3.toml", f'id = "X3"\nquestion = "{QUESTION}"\npasses = 0\n')
        with self.assertRaises(ValueError) as caught:
            load_task(path)
        self.assertEqual(str(caught.exception), "X3.toml: passes must be a whole number of at least 1")


if __name__ == "__main__":
    unittest.main()
