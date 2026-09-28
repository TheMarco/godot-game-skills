import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


installer = module("installer", "scripts/install.py")
timings = module("timings", "skills/godot-performance-workflows/scripts/compare_timings.py")


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source" / "skill-one"
        self.source.mkdir(parents=True)
        (self.source / "SKILL.md").write_text("new skill")
        self.dest = self.root / "installed"

    def test_install_is_self_contained_and_omits_cache(self):
        (self.source / ".godot").mkdir()
        (self.source / ".godot" / "cache").write_text("generated")
        installer.install({"skill-one": self.source}, self.dest)
        self.assertEqual((self.dest / "skill-one" / "SKILL.md").read_text(), "new skill")
        self.assertFalse((self.dest / "skill-one" / ".godot").exists())

    def test_existing_install_preserved_and_force_keeps_backup(self):
        existing = self.dest / "skill-one"
        existing.mkdir(parents=True)
        (existing / "SKILL.md").write_text("user edit")
        installer.install({"skill-one": self.source}, self.dest)
        self.assertEqual((existing / "SKILL.md").read_text(), "user edit")
        installer.install({"skill-one": self.source}, self.dest, force=True)
        self.assertEqual((existing / "SKILL.md").read_text(), "new skill")
        backups = list((self.dest / ".godot-game-skills-backups").glob("*/SKILL.md"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), "user edit")

    def test_dry_run_creates_nothing(self):
        installer.install({"skill-one": self.source}, self.dest, dry_run=True)
        self.assertFalse(self.dest.exists())

    def test_source_destination_overlap_rejected(self):
        with self.assertRaises(ValueError):
            installer.install({"skill-one": self.source}, self.source.parent)

    def test_unknown_skill_does_not_create_destination(self):
        self.assertEqual(installer.main(["--dest", str(self.dest), "--skill", "unknown"]), 2)
        self.assertFalse(self.dest.exists())


class TimingTests(unittest.TestCase):
    def series(self, values):
        return {"metric": "build_cpu", "unit": "ms", "context": {"seed": 7}, "samples": values}

    def test_tail_and_mean_are_separate(self):
        report = timings.compare(self.series([1] * 19 + [100]), self.series([2] * 20))
        self.assertLess(report["change"]["mean"]["absolute"], 0)
        self.assertGreater(report["change"]["p95"]["absolute"], 0)
        self.assertLess(report["change"]["max"]["absolute"], 0)

    def test_incompatible_context_rejected(self):
        after = self.series([2])
        after["context"]["seed"] = 8
        with self.assertRaisesRegex(ValueError, "context"):
            timings.compare(self.series([3]), after)

    def test_zero_baseline_has_no_percentage(self):
        report = timings.compare(self.series([0]), self.series([1]))
        self.assertIsNone(report["change"]["mean"]["percent"])

    def test_nonfinite_negative_and_boolean_samples_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "series.json"
            for value in [True, -1, float("nan"), float("inf")]:
                path.write_text(json.dumps(self.series([value])))
                with self.assertRaises(ValueError):
                    timings.load_series(path)


if __name__ == "__main__":
    unittest.main()
