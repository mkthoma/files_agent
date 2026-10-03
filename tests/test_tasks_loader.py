import tempfile
import unittest
from pathlib import Path

from harness.tasks import load_all, load_task


def write_toml(folder, name, body):
    path = Path(folder) / name
    path.write_text(body, encoding="utf-8")
    return path


class TaskLoaderTest(unittest.TestCase):
    def test_unknown_expect_key_raises(self):
        with tempfile.TemporaryDirectory() as d:
            path = write_toml(d, "a.toml", 'id = "x"\nquestion = "q"\n[expect]\nnonsense = 1\n')
            with self.assertRaises(ValueError):
                load_task(path)

    def test_bad_mode_raises(self):
        with tempfile.TemporaryDirectory() as d:
            path = write_toml(d, "a.toml", 'id = "x"\nquestion = "q"\nmode = "write"\n')
            with self.assertRaises(ValueError):
                load_task(path)

    def test_only_one_live_write_task(self):
        with tempfile.TemporaryDirectory() as d:
            body = 'id = "{tid}"\nquestion = "q"\nlive_write = true\nlive_allowlist = true\n'
            write_toml(d, "a.toml", body.format(tid="a"))
            write_toml(d, "b.toml", body.format(tid="b"))
            with self.assertRaises(ValueError):
                load_all(Path(d))

    def test_live_write_needs_an_allowlist(self):
        with tempfile.TemporaryDirectory() as d:
            write_toml(d, "a.toml", 'id = "a"\nquestion = "q"\nlive_write = true\n')
            with self.assertRaises(ValueError):
                load_all(Path(d))

    def test_good_file_loads(self):
        with tempfile.TemporaryDirectory() as d:
            path = write_toml(d, "a.toml", 'id = "a"\nquestion = "q"\nmode = "apply"\npasses = 2\n')
            task = load_task(path)
            self.assertEqual(task.mode, "apply")
            self.assertEqual(task.passes, 2)
            self.assertIsInstance(task.faults, tuple)


if __name__ == "__main__":
    unittest.main()
