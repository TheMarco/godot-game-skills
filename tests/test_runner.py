"""Unit tests for skills/godot-game-verification/scripts/run_checks.py.

Loads the runner by file path (no package import) and drives it with fake
Godot engines (small Python scripts run through ``sys.executable``), so no
Godot binary is needed.
"""

import importlib.util
import json
import os
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest

RUNNER_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "skills",
    "godot-game-verification", "scripts", "run_checks.py")


def load_runner():
    spec = importlib.util.spec_from_file_location("run_checks", RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


run_checks = load_runner()

# Fake Godot engine: behaviour is driven by environment variables so each
# test can script exit codes, markers, errors, hangs, and import failures.
FAKE_GODOT = """\
import os, sys, time
argv = sys.argv[1:]
if "--version" in argv:
    time.sleep(float(os.environ.get("FAKE_VERSION_SLEEP", "0")))
    print(os.environ.get("FAKE_VERSION_TEXT",
                         "Godot Engine v4.3.stable.official.test"))
    sys.exit(int(os.environ.get("FAKE_VERSION_EXIT", "0")))
if "--import" in argv:
    text = os.environ.get("FAKE_IMPORT_TEXT", "")
    if text:
        print(text)
    sys.exit(int(os.environ.get("FAKE_IMPORT_EXIT", "0")))
sleep = float(os.environ.get("FAKE_SLEEP", "0"))
if sleep:
    time.sleep(sleep)
marker = os.environ.get("FAKE_MARKER", "")
if marker:
    print(marker)
error = os.environ.get("FAKE_ERROR", "")
if error:
    print(error)
sys.exit(int(os.environ.get("FAKE_EXIT", "0")))
"""


class RunnerTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = self.tmp.name
        self.project = os.path.join(self.root, "proj")
        os.makedirs(os.path.join(self.project, "checks"))
        with open(os.path.join(self.project, "project.godot"), "w") as f:
            f.write("; fixture\n")
        with open(os.path.join(self.project, "checks", "demo.gd"), "w") as f:
            f.write("extends SceneTree\n")
        self.fake_godot = os.path.join(self.root, "fake-godot")
        with open(self.fake_godot, "w") as f:
            f.write("#!%s\n%s" % (sys.executable, FAKE_GODOT))
        os.chmod(self.fake_godot, 0o755)
        self.outbase = os.path.join(self.root, "out")

    def write_manifest(self, manifest):
        path = os.path.join(self.root, "manifest.json")
        with open(path, "w") as f:
            json.dump(manifest, f)
        return path

    def base_manifest(self, **overrides):
        check = {"name": "determinism",
                 "script": "res://checks/demo.gd",
                 "args": [],
                 "success_marker": "PASS: determinism",
                 "timeout": 10}
        check.update(overrides)
        return {"version": 1, "checks": [check]}

    def run_cli(self, *extra, env=None, cwd=None):
        full_env = dict(os.environ)
        full_env.update(env or {})
        cmd = [sys.executable, RUNNER_PATH,
               "--project", self.project,
               "--manifest", os.path.join(self.root, "manifest.json"),
               "--godot", self.fake_godot,
               "--output", self.outbase] + list(extra)
        return subprocess.run(cmd, capture_output=True, text=True,
                              env=full_env, cwd=cwd or self.root,
                              timeout=120)

    def run_dirs(self):
        return sorted(
            os.path.join(self.outbase, d) for d in os.listdir(self.outbase)
            if os.path.isdir(os.path.join(self.outbase, d)))

    def read_report(self, index=0):
        with open(os.path.join(self.run_dirs()[index], "metadata",
                               "report.json")) as f:
            return json.load(f)

    def run_path(self, *parts, index=0):
        return os.path.join(self.run_dirs()[index], *parts)


class ManifestValidationTests(RunnerTestCase):
    def validate(self, manifest, timeout=60.0):
        return run_checks.validate_manifest(manifest, self.project, timeout)

    def test_valid_manifest(self):
        checks = self.validate(self.base_manifest())
        self.assertEqual(len(checks), 1)
        self.assertEqual(checks[0]["name"], "determinism")
        self.assertTrue(checks[0]["script_path"].endswith("demo.gd"))

    def test_unknown_top_level_field_rejected(self):
        manifest = self.base_manifest()
        manifest["extra"] = 1
        with self.assertRaises(run_checks.ManifestError):
            self.validate(manifest)

    def test_unknown_check_field_rejected(self):
        with self.assertRaises(run_checks.ManifestError):
            self.validate(self.base_manifest(bogus=True))

    def test_bad_version_rejected(self):
        with self.assertRaises(run_checks.ManifestError):
            self.validate({"version": 2, "checks": []})

    def test_version_must_be_exact_int(self):
        for bad in [1.0, True, "1", None]:
            with self.subTest(version=bad):
                with self.assertRaises(run_checks.ManifestError):
                    self.validate({"version": bad,
                                   "checks": self.base_manifest()["checks"]})

    def test_empty_checks_rejected(self):
        with self.assertRaises(run_checks.ManifestError):
            self.validate({"version": 1, "checks": []})

    def test_duplicate_names_rejected(self):
        manifest = self.base_manifest()
        manifest["checks"].append(dict(manifest["checks"][0]))
        with self.assertRaises(run_checks.ManifestError):
            self.validate(manifest)

    def test_case_insensitive_duplicate_names_rejected(self):
        manifest = self.base_manifest(name="Alpha")
        manifest["checks"].append(dict(manifest["checks"][0], name="alpha"))
        with self.assertRaises(run_checks.ManifestError):
            self.validate(manifest)

    def test_invocation_like_names_allowed(self):
        # Log files are prefixed with "check-", so these cannot collide
        # with version.log / import.log.
        for name in ["version", "import", "Import", "import-godot"]:
            with self.subTest(name=name):
                checks = self.validate(self.base_manifest(name=name))
                self.assertEqual(checks[0]["name"], name)

    def test_unsafe_names_rejected(self):
        for bad in ["", "../x", "a/b", "a\\b", ".", "..", "-x", "has space"]:
            with self.subTest(name=bad):
                with self.assertRaises(run_checks.ManifestError):
                    self.validate(self.base_manifest(name=bad))

    def test_empty_marker_rejected(self):
        with self.assertRaises(run_checks.ManifestError):
            self.validate(self.base_manifest(success_marker=""))

    def test_blank_or_multiline_marker_rejected(self):
        for bad in ["   ", "\t ", "ok\nPASS", "PASS: x\r\n", "a\rb"]:
            with self.subTest(marker=bad):
                with self.assertRaises(run_checks.ManifestError):
                    self.validate(self.base_manifest(success_marker=bad))

    def test_args_must_be_string_list(self):
        with self.assertRaises(run_checks.ManifestError):
            self.validate(self.base_manifest(args="--x"))
        with self.assertRaises(run_checks.ManifestError):
            self.validate(self.base_manifest(args=[1]))

    def test_path_traversal_rejected(self):
        with self.assertRaises(run_checks.ManifestError):
            self.validate(self.base_manifest(
                script="res://checks/../../outside.gd"))

    def test_missing_script_rejected(self):
        with self.assertRaises(run_checks.ManifestError):
            self.validate(self.base_manifest(script="res://checks/nope.gd"))

    def test_non_gd_script_rejected(self):
        with self.assertRaises(run_checks.ManifestError):
            self.validate(self.base_manifest(script="res://checks/demo.txt"))

    def test_non_res_script_rejected(self):
        with self.assertRaises(run_checks.ManifestError):
            self.validate(self.base_manifest(script="checks/demo.gd"))

    def test_bad_timeouts_rejected(self):
        for bad in [0, -1, "soon", float("nan"), float("inf"), None,
                    True, False]:
            with self.subTest(timeout=bad):
                with self.assertRaises(run_checks.ManifestError):
                    self.validate(self.base_manifest(timeout=bad))


class ScanLogTests(RunnerTestCase):
    def scan(self, content, marker=None):
        path = os.path.join(self.root, "sample.log")
        with open(path, "w") as f:
            f.write(content)
        return run_checks.scan_log(path, marker)

    def test_clean_log(self):
        found, errors, count = self.scan("hello\nPASS: x\n", "PASS: x")
        self.assertTrue(found)
        self.assertEqual(count, 0)
        self.assertEqual(errors, [])

    def test_script_error_detected(self):
        _, _, count = self.scan("SCRIPT ERROR: bad\n")
        self.assertEqual(count, 1)

    def test_parse_and_compile_errors_detected(self):
        _, _, count = self.scan("Parse Error here\nCompile Error there\n")
        self.assertEqual(count, 2)

    def test_indented_and_ansi_errors_detected(self):
        _, _, count = self.scan("  ERROR: indented\n")
        self.assertEqual(count, 1)
        _, _, count = self.scan("\t\x1b[31mERROR: colored\x1b[0m\n")
        self.assertEqual(count, 1)
        _, _, count = self.scan("\x1b[1mSCRIPT ERROR: colored\x1b[0m\n")
        self.assertEqual(count, 1)

    def test_leak_warnings_detected(self):
        _, _, count = self.scan("ObjectDB instances leaked: 3\n")
        self.assertEqual(count, 1)
        _, _, count = self.scan("resources still in use at exit\n")
        self.assertEqual(count, 1)


class EndToEndTests(RunnerTestCase):
    def test_success(self):
        self.write_manifest(self.base_manifest())
        proc = self.run_cli(env={"FAKE_MARKER": "PASS: determinism"})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        report = self.read_report()
        self.assertEqual(report["summary"], {"selected": 1, "passed": 1,
                                             "failed": 0})
        self.assertTrue(report["checks"][0]["marker_found"])
        self.assertIn("Godot Engine", report["engine_version"])
        self.assertIn("report:", proc.stdout)
        self.assertTrue(os.path.isfile(
            self.run_path("logs", "check-determinism.log")))
        self.assertTrue(os.path.isabs(report["run_dir"]))

    def test_nonzero_exit_fails(self):
        self.write_manifest(self.base_manifest())
        proc = self.run_cli(env={"FAKE_MARKER": "PASS: determinism",
                                 "FAKE_EXIT": "3"})
        self.assertEqual(proc.returncode, 1)
        report = self.read_report()
        self.assertFalse(report["checks"][0]["passed"])
        self.assertEqual(report["checks"][0]["exit_code"], 3)

    def test_zero_exit_script_error_fails(self):
        self.write_manifest(self.base_manifest())
        proc = self.run_cli(env={"FAKE_MARKER": "PASS: determinism",
                                 "FAKE_ERROR": "SCRIPT ERROR: boom"})
        self.assertEqual(proc.returncode, 1)
        report = self.read_report()
        self.assertEqual(report["checks"][0]["error_count"], 1)
        self.assertFalse(report["checks"][0]["passed"])

    def test_colored_error_fails(self):
        self.write_manifest(self.base_manifest())
        proc = self.run_cli(env={"FAKE_MARKER": "PASS: determinism",
                                 "FAKE_ERROR": "\x1b[31mERROR: boom\x1b[0m"})
        self.assertEqual(proc.returncode, 1)
        self.assertFalse(self.read_report()["checks"][0]["passed"])

    def test_missing_marker_fails(self):
        self.write_manifest(self.base_manifest())
        proc = self.run_cli(env={"FAKE_MARKER": "something else"})
        self.assertEqual(proc.returncode, 1)
        self.assertFalse(self.read_report()["checks"][0]["marker_found"])

    def test_hanging_check_times_out(self):
        self.write_manifest(self.base_manifest(timeout=1))
        proc = self.run_cli(env={"FAKE_SLEEP": "30",
                                 "FAKE_MARKER": "PASS: determinism"})
        self.assertEqual(proc.returncode, 1)
        check = self.read_report()["checks"][0]
        self.assertTrue(check["timed_out"])
        self.assertLess(check["elapsed"], 20)

    def test_invalid_manifest_cli_error(self):
        self.write_manifest({"version": 1, "checks": []})
        proc = self.run_cli()
        self.assertEqual(proc.returncode, 2)
        self.assertIn("nonempty", proc.stderr)

    def test_filter_no_match_fails(self):
        self.write_manifest(self.base_manifest())
        proc = self.run_cli("--filter", "zzz-no-such-check")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("matched no checks", proc.stderr)

    def test_filter_selects_subset(self):
        manifest = self.base_manifest()
        second = dict(manifest["checks"][0], name="other",
                      success_marker="PASS: other")
        manifest["checks"].append(second)
        self.write_manifest(manifest)
        proc = self.run_cli("--filter", "other",
                            env={"FAKE_MARKER": "PASS: other"})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(self.read_report()["summary"]["selected"], 1)

    def test_import_failure_prevents_checks(self):
        self.write_manifest(self.base_manifest())
        proc = self.run_cli(env={"FAKE_IMPORT_EXIT": "1",
                                 "FAKE_MARKER": "PASS: determinism"})
        self.assertEqual(proc.returncode, 1)
        report = self.read_report()
        self.assertFalse(report["import"]["passed"])
        self.assertTrue(report["checks"][0].get("skipped"))
        self.assertFalse(os.path.exists(
            self.run_path("logs", "check-determinism.log")))

    def test_missing_project_godot_fails(self):
        os.remove(os.path.join(self.project, "project.godot"))
        self.write_manifest(self.base_manifest())
        proc = self.run_cli()
        self.assertEqual(proc.returncode, 2)
        self.assertIn("project.godot", proc.stderr)

    def test_relative_manifest_resolves_from_cwd(self):
        self.write_manifest(self.base_manifest())
        full_env = dict(os.environ, FAKE_MARKER="PASS: determinism")
        cmd = [sys.executable, RUNNER_PATH,
               "--project", "proj",
               "--manifest", "manifest.json",
               "--godot", self.fake_godot,
               "--output", "out"]
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              env=full_env, cwd=self.root, timeout=120)
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_default_output_never_deletes(self):
        self.write_manifest(self.base_manifest())
        keep = os.path.join(self.project, "artifacts", "checks", "keep.txt")
        os.makedirs(os.path.dirname(keep))
        with open(keep, "w") as f:
            f.write("keep")
        full_env = dict(os.environ, FAKE_MARKER="PASS: determinism")
        cmd = [sys.executable, RUNNER_PATH,
               "--project", self.project,
               "--manifest", os.path.join(self.root, "manifest.json"),
               "--godot", self.fake_godot]
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              env=full_env, timeout=120)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(os.path.isfile(keep))

    def test_output_base_gets_fresh_child_per_run(self):
        self.write_manifest(self.base_manifest())
        first = self.run_cli(env={"FAKE_MARKER": "PASS: determinism"})
        self.assertEqual(first.returncode, 0, first.stderr)
        # Second run emits no marker: a stale marker from the first run's
        # logs must not leak over and pass it.
        second = self.run_cli(env={})
        self.assertEqual(second.returncode, 1, second.stderr)
        self.assertEqual(len(self.run_dirs()), 2)
        for index in (0, 1):
            self.assertTrue(os.path.isfile(
                self.run_path("metadata", "report.json", index=index)))

    def test_version_named_check_does_not_collide(self):
        self.write_manifest(self.base_manifest(
            name="version", success_marker="PASS: version"))
        proc = self.run_cli(env={"FAKE_MARKER": "PASS: version"})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(os.path.isfile(
            self.run_path("logs", "check-version.log")))
        with open(self.run_path("logs", "version.log")) as f:
            self.assertIn("Godot Engine", f.read())

    def test_engine_log_suffix_cannot_collide_with_another_check(self):
        manifest = self.base_manifest(name="sample", success_marker="PASS: fixture")
        manifest["checks"].append(dict(manifest["checks"][0], name="sample-godot"))
        self.write_manifest(manifest)
        proc = self.run_cli(env={"FAKE_MARKER": "PASS: fixture"})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        records = self.read_report()["checks"]
        paths = [record[key] for record in records for key in ("log", "godot_log")]
        self.assertEqual(len(set(paths)), 4)

    def test_failed_probe_fails_run_with_report(self):
        self.write_manifest(self.base_manifest())
        proc = self.run_cli(env={"FAKE_VERSION_EXIT": "1",
                                 "FAKE_MARKER": "PASS: determinism"})
        self.assertEqual(proc.returncode, 1)
        self.assertIn("probe FAILED", proc.stdout)
        report = self.read_report()
        self.assertFalse(report["engine_probe"]["passed"])
        self.assertIsNone(report["import"])
        self.assertTrue(report["checks"][0].get("skipped"))
        self.assertFalse(os.path.exists(self.run_path("logs", "import.log")))

    def test_empty_probe_fails_run(self):
        self.write_manifest(self.base_manifest())
        proc = self.run_cli(env={"FAKE_VERSION_TEXT": "",
                                 "FAKE_MARKER": "PASS: determinism"})
        self.assertEqual(proc.returncode, 1)
        report = self.read_report()
        self.assertIsNone(report["engine_version"])
        self.assertTrue(report["checks"][0].get("skipped"))

    def test_probe_timeout_fails_run(self):
        self.write_manifest(self.base_manifest())
        old_timeout = run_checks.PROBE_TIMEOUT
        run_checks.PROBE_TIMEOUT = 1
        self.addCleanup(setattr, run_checks, "PROBE_TIMEOUT", old_timeout)
        full_env = dict(os.environ, FAKE_VERSION_SLEEP="30",
                        FAKE_MARKER="PASS: determinism")
        old_env = dict(os.environ)
        os.environ.update(full_env)
        self.addCleanup(lambda: os.environ.clear() or os.environ.update(old_env))
        rc = run_checks.main(["--project", self.project,
                              "--manifest",
                              os.path.join(self.root, "manifest.json"),
                              "--godot", self.fake_godot,
                              "--output", self.outbase])
        self.assertEqual(rc, 1)
        report = self.read_report()
        self.assertTrue(report["engine_probe"]["timed_out"])
        self.assertTrue(report["checks"][0].get("skipped"))

    def test_missing_binary_fails_cleanly_with_report(self):
        self.write_manifest(self.base_manifest())
        full_env = dict(os.environ, FAKE_MARKER="PASS: determinism")
        cmd = [sys.executable, RUNNER_PATH,
               "--project", self.project,
               "--manifest", os.path.join(self.root, "manifest.json"),
               "--godot", os.path.join(self.root, "no-such-godot"),
               "--output", self.outbase]
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              env=full_env, timeout=120)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("not found", proc.stdout)
        self.assertNotIn("Traceback", proc.stdout + proc.stderr)
        report = self.read_report()
        self.assertFalse(report["engine_probe"]["passed"])
        self.assertTrue(report["checks"][0].get("skipped"))


class InterruptTests(RunnerTestCase):
    @unittest.skipUnless(os.name == "posix", "POSIX process groups only")
    def test_interrupt_kills_child_and_group(self):
        script = os.path.join(self.root, "sleeper.py")
        pidfile = os.path.join(self.root, "pids.txt")
        log = os.path.join(self.root, "interrupt.log")
        with open(script, "w") as f:
            f.write(
                "import os, subprocess, sys, time\n"
                "grandchild = subprocess.Popen(\n"
                "    [sys.executable, '-c', 'import time; time.sleep(30)'])\n"
                f"open({pidfile!r}, 'w').write(\n"
                "    f'{os.getpid()} {grandchild.pid}')\n"
                "time.sleep(30)\n")
        timer = threading.Timer(
            1.0, lambda: os.kill(os.getpid(), signal.SIGINT))
        timer.start()
        try:
            with self.assertRaises(KeyboardInterrupt):
                run_checks.run_bounded([sys.executable, script], 30, log)
        finally:
            timer.cancel()
        with open(pidfile) as f:
            pids = [int(p) for p in f.read().split()]
        self.assertEqual(len(pids), 2)
        time.sleep(0.5)  # let SIGKILL land before asserting
        for pid in pids:
            with self.subTest(pid=pid):
                with self.assertRaises(ProcessLookupError):
                    os.kill(pid, 0)


if __name__ == "__main__":
    unittest.main()
