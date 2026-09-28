#!/usr/bin/env python3
"""Run portable Godot headless verification checks from a JSON manifest.

Sequential, stdlib-only runner. Each check is a Godot ``--script`` invocation
whose combined output must contain a success marker and no unexpected engine
errors. A full report plus per-check logs is written under the output
directory; nothing already there is ever deleted.

Timeout enforcement: on POSIX each child runs in its own process session
(``start_new_session=True``) and the whole group is killed on timeout. On
Windows the runner falls back to killing the direct child only (see
``references/checks.md`` ``Timeouts``); grandchildren may outlive a timeout
there.
"""

from __future__ import annotations

import argparse
import datetime
import json
import math
import os
import re
import signal
import subprocess
import sys
import time

MANIFEST_VERSION = 1
DEFAULT_TIMEOUT = 60.0
PROBE_TIMEOUT = 30.0
RUNNER_VERSION = 1

TOP_LEVEL_FIELDS = frozenset({"version", "checks"})
CHECK_FIELDS = frozenset({"name", "script", "args", "success_marker", "timeout"})
NAME_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")

# Substrings that always fail a check (or the import pass) when present.
# Documented in references/checks.md; there are no global suppressions.
ERROR_SUBSTRINGS = (
    "SCRIPT ERROR",
    "Parse Error",
    "Compile Error",
    "ObjectDB instances leaked",
    "resources still in use at exit",
)
ERROR_LINE_PREFIX = "ERROR:"
ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")

# Bound on error lines copied into report.json; full logs stay on disk.
MAX_REPORT_ERROR_LINES = 20


class ManifestError(ValueError):
    """Raised when a manifest or its references are invalid."""


def parse_timeout(value) -> float:
    """Return *value* as a finite positive number of seconds."""
    if isinstance(value, bool):
        raise ManifestError(
            f"timeout must be a number of seconds, got {value!r}")
    try:
        timeout = float(value)
    except (TypeError, ValueError):
        raise ManifestError(f"timeout must be a number of seconds, got {value!r}")
    if not math.isfinite(timeout) or timeout <= 0:
        raise ManifestError(f"timeout must be finite and positive, got {value!r}")
    return timeout


def check_name_ok(name) -> bool:
    return isinstance(name, str) and bool(NAME_RE.match(name))


def resolve_script(project_dir: str, script: str) -> str:
    """Map a ``res://`` script path to an existing ``.gd`` file in the project."""
    if not isinstance(script, str) or not script.startswith("res://"):
        raise ManifestError(
            f"script must be a res:// path, got {script!r}")
    rel = script[len("res://"):]
    if not rel.endswith(".gd"):
        raise ManifestError(f"script must be a .gd file, got {script!r}")
    candidate = os.path.realpath(os.path.join(project_dir, rel))
    root = os.path.realpath(project_dir)
    if os.path.commonpath([root, candidate]) != root or candidate == root:
        raise ManifestError(
            f"script escapes the project directory: {script!r}")
    if not os.path.isfile(candidate):
        raise ManifestError(
            f"script does not exist in project: {script!r}")
    return candidate


def validate_manifest(data, project_dir: str, default_timeout: float) -> list:
    """Validate parsed manifest JSON; return normalized check dicts."""
    if not isinstance(data, dict):
        raise ManifestError("manifest root must be a JSON object")
    unknown = set(data) - TOP_LEVEL_FIELDS
    if unknown:
        raise ManifestError(
            f"unknown manifest field(s): {sorted(unknown)}")
    version = data.get("version")
    if type(version) is not int or version != MANIFEST_VERSION:
        raise ManifestError(
            f"manifest version must be {MANIFEST_VERSION}, "
            f"got {version!r}")
    checks = data.get("checks")
    if not isinstance(checks, list) or not checks:
        raise ManifestError("manifest must define a nonempty 'checks' list")
    seen = set()
    normalized = []
    for index, entry in enumerate(checks):
        where = f"checks[{index}]"
        if not isinstance(entry, dict):
            raise ManifestError(f"{where} must be an object")
        unknown = set(entry) - CHECK_FIELDS
        if unknown:
            raise ManifestError(
                f"{where} has unknown field(s): {sorted(unknown)}")
        name = entry.get("name")
        if not check_name_ok(name):
            raise ManifestError(
                f"{where}.name must be a safe file basename "
                f"(letter/digit start, then letters, digits, '.', '_' or '-'), "
                f"got {name!r}")
        folded = name.lower()
        if folded in seen:
            raise ManifestError(
                f"duplicate check name (case-insensitive): {name!r}")
        seen.add(folded)
        script_path = resolve_script(project_dir, entry.get("script"))
        args = entry.get("args", [])
        if not isinstance(args, list) or any(
                not isinstance(a, str) for a in args):
            raise ManifestError(f"{where}.args must be a list of strings")
        marker = entry.get("success_marker")
        if (not isinstance(marker, str) or not marker.strip()
                or "\n" in marker or "\r" in marker):
            raise ManifestError(
                f"{where}.success_marker must be a nonempty single-line "
                f"string with non-whitespace content")
        timeout = default_timeout
        if "timeout" in entry:
            try:
                timeout = parse_timeout(entry["timeout"])
            except ManifestError as exc:
                raise ManifestError(f"{where}.timeout: {exc}")
        normalized.append({
            "name": name,
            "script": entry["script"],
            "script_path": script_path,
            "args": list(args),
            "success_marker": marker,
            "timeout": timeout,
        })
    return normalized


def load_manifest(manifest_path: str, project_dir: str,
                  default_timeout: float) -> list:
    try:
        with open(manifest_path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        raise ManifestError(f"manifest not found: {manifest_path}")
    except json.JSONDecodeError as exc:
        raise ManifestError(f"manifest is not valid JSON: {exc}")
    return validate_manifest(data, project_dir, default_timeout)


def normalize_log_line(line: str) -> str:
    """Strip ANSI color sequences and leading whitespace for error matching."""
    return ANSI_RE.sub("", line).lstrip()


def is_error_line(line: str) -> bool:
    text = normalize_log_line(line)
    if text.startswith(ERROR_LINE_PREFIX):
        return True
    return any(token in text for token in ERROR_SUBSTRINGS)


def scan_log(log_path: str, marker: str | None = None):
    """Stream a log file; return (marker_found, error_lines, error_count).

    The file is read line by line so arbitrarily large logs stay on disk;
    only the first ``MAX_REPORT_ERROR_LINES`` matches are kept.
    """
    found = False
    errors: list = []
    count = 0
    with open(log_path, "r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            text = line.rstrip("\n")
            if marker is not None and not found and marker in text:
                found = True
            if is_error_line(text):
                count += 1
                if len(errors) < MAX_REPORT_ERROR_LINES:
                    errors.append(text[:500])
    return found, errors, count


def run_bounded(argv: list, timeout: float, log_path: str) -> dict:
    """Run *argv* with combined output written to *log_path*.

    No shell interpolation. On POSIX the child starts a new session so a
    timeout kills the whole process group; on Windows only the direct
    child is terminated (documented limitation). An interrupt during the
    wait terminates the owned child (or group) before propagating.
    """
    timeout = parse_timeout(timeout)
    start = time.monotonic()
    timed_out = False
    popen_kwargs = {
        "stdin": subprocess.DEVNULL,
        "stderr": subprocess.STDOUT,
    }
    if os.name == "posix":
        popen_kwargs["start_new_session"] = True
    elif hasattr(subprocess, "CREATE_NEW_PROCESS_GROUP"):
        popen_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    with open(log_path, "wb") as log:
        proc = subprocess.Popen(argv, stdout=log, **popen_kwargs)
        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            _kill_child(proc)
            proc.wait()
        except BaseException:
            _kill_child(proc)
            proc.wait()
            raise
        elapsed = time.monotonic() - start
        if timed_out:
            log.write(
                f"\n--- killed after {timeout:g}s (timeout) ---\n".encode())
    return {
        "argv": list(argv),
        "exit_code": proc.returncode,
        "timed_out": timed_out,
        "elapsed": round(elapsed, 3),
    }


def _kill_child(proc: "subprocess.Popen") -> None:
    if os.name == "posix":
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            return
        except (ProcessLookupError, PermissionError, OSError):
            pass
    proc.kill()


def probe_engine_version(godot: str, log_path: str) -> dict:
    result = run_bounded([godot, "--version"], PROBE_TIMEOUT, log_path)
    version = None
    if not result["timed_out"] and result["exit_code"] == 0:
        try:
            with open(log_path, "r", encoding="utf-8",
                      errors="replace") as handle:
                version = handle.readline().strip()[:200] or None
        except OSError:
            version = None
    _, errors, error_count = scan_log(log_path)
    result["version"] = version
    result["errors"] = errors
    result["error_count"] = error_count
    result["log"] = log_path
    result["passed"] = (
        not result["timed_out"]
        and result["exit_code"] == 0
        and version is not None
        and error_count == 0
    )
    return result


def run_import(godot: str, project_dir: str, timeout: float, log_path: str,
               godot_log_path: str) -> dict:
    argv = [godot, "--headless", "--path", project_dir,
           "--log-file", godot_log_path, "--import"]
    result = run_bounded(argv, timeout, log_path)
    _, errors, error_count = scan_log(log_path)
    result["errors"] = errors
    result["error_count"] = error_count
    result["log"] = log_path
    result["godot_log"] = godot_log_path
    result["passed"] = (
        not result["timed_out"]
        and result["exit_code"] == 0
        and error_count == 0
    )
    return result


def run_check(godot: str, project_dir: str, check: dict,
              log_path: str, godot_log_path: str) -> dict:
    argv = [godot, "--headless", "--path", project_dir,
            "--log-file", godot_log_path,
            "--script", check["script_path"]]
    if check["args"]:
        argv += ["--"] + check["args"]
    result = run_bounded(argv, check["timeout"], log_path)
    marker_found, errors, error_count = scan_log(
        log_path, check["success_marker"])
    result["name"] = check["name"]
    result["marker_found"] = marker_found
    result["errors"] = errors
    result["error_count"] = error_count
    result["log"] = log_path
    result["godot_log"] = godot_log_path
    result["passed"] = (
        not result["timed_out"]
        and result["exit_code"] == 0
        and error_count == 0
        and marker_found
    )
    reasons = []
    if result["timed_out"]:
        reasons.append("timeout")
    elif result["exit_code"] != 0:
        reasons.append(f"exit {result['exit_code']}")
    if error_count:
        reasons.append(f"{error_count} error(s)")
    if not marker_found:
        reasons.append("missing success marker")
    result["reasons"] = reasons
    return result


def make_run_dir(project_dir: str, output: str | None) -> str:
    """Create a fresh unique run dir inside the output base directory.

    *project_dir* must be absolute so every derived log path is absolute.
    *output* is a base directory, never the run dir itself: each run gets
    a new unique child, so stale logs or markers can never leak across runs.
    Existing output is never deleted.
    """
    if output:
        base = os.path.abspath(output)
    else:
        base = os.path.join(project_dir, "artifacts", "checks")
    if os.path.exists(base) and not os.path.isdir(base):
        raise ManifestError(f"output base is not a directory: {base}")
    try:
        os.makedirs(base, exist_ok=True)
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y%m%dT%H%M%SZ")
        candidate = os.path.join(base, f"{stamp}-pid{os.getpid()}")
        suffix = 0
        while os.path.exists(candidate):
            suffix += 1
            candidate = os.path.join(
                base, f"{stamp}-pid{os.getpid()}-{suffix}")
        os.makedirs(candidate)
    except OSError as exc:
        raise ManifestError(f"cannot create output directory: {exc}")
    return candidate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run Godot headless checks from a JSON manifest.")
    parser.add_argument("--project", required=True,
                        help="Godot project dir (must contain project.godot)")
    parser.add_argument("--manifest", required=True,
                        help="manifest JSON path (relative to caller CWD)")
    parser.add_argument("--godot",
                        default=os.environ.get("GODOT", "godot"),
                        help="Godot binary (default: $GODOT or 'godot')")
    parser.add_argument("--filter", default=None,
                        help="run only checks whose name contains SUBSTRING")
    parser.add_argument("--timeout", default=DEFAULT_TIMEOUT,
                        help="default per-invocation timeout in seconds "
                             "(default: 60)")
    parser.add_argument("--skip-import", action="store_true",
                        help="skip the one-time editor import pass")
    parser.add_argument("--output", default=None,
                        help="output BASE dir; a fresh unique run dir is "
                             "always created inside it (default base: "
                             "project/artifacts/checks)")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)

    try:
        default_timeout = parse_timeout(args.timeout)
    except ManifestError as exc:
        print(f"error: --timeout: {exc}", file=sys.stderr)
        return 2

    project_dir = os.path.abspath(args.project)
    if not os.path.isfile(os.path.join(project_dir, "project.godot")):
        print(f"error: project has no project.godot: {args.project}",
              file=sys.stderr)
        return 2
    manifest_path = os.path.abspath(args.manifest)
    try:
        checks = load_manifest(manifest_path, project_dir, default_timeout)
    except ManifestError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.filter is not None:
        checks = [c for c in checks if args.filter in c["name"]]
        if not checks:
            print(f"error: --filter matched no checks: {args.filter!r}",
                  file=sys.stderr)
            return 2

    try:
        run_dir = make_run_dir(project_dir, args.output)
    except ManifestError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    logs_dir = os.path.join(run_dir, "logs")
    meta_dir = os.path.join(run_dir, "metadata")
    try:
        os.makedirs(logs_dir, exist_ok=True)
        os.makedirs(meta_dir, exist_ok=True)
    except OSError as exc:
        print(f"error: cannot create run directories: {exc}", file=sys.stderr)
        return 2
    report_path = os.path.join(meta_dir, "report.json")

    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    version_log = os.path.join(logs_dir, "version.log")
    try:
        probe = probe_engine_version(args.godot, version_log)
    except FileNotFoundError:
        probe = {"argv": [args.godot, "--version"], "exit_code": None,
                 "timed_out": False, "elapsed": 0.0, "version": None,
                 "errors": [], "error_count": 0, "log": version_log,
                 "passed": False,
                 "error": f"godot binary not found: {args.godot}"}
    except OSError as exc:
        probe = {"argv": [args.godot, "--version"], "exit_code": None,
                 "timed_out": False, "elapsed": 0.0, "version": None,
                 "errors": [], "error_count": 0, "log": version_log,
                 "passed": False,
                 "error": f"cannot run godot binary {args.godot}: {exc}"}

    results = []
    import_result = None
    failed = False
    if not probe["passed"]:
        failed = True
        detail = probe.get("error") or f"see {version_log}"
        print(f"engine probe FAILED ({detail}); import and checks "
              f"will not run")
        for check in checks:
            results.append({"name": check["name"], "passed": False,
                            "reasons": ["skipped: engine probe failed"],
                            "skipped": True})
    else:
        if not args.skip_import:
            import_result = run_import(
                args.godot, project_dir, default_timeout,
                os.path.join(logs_dir, "import.log"),
                os.path.join(logs_dir, "import-godot.log"))
            if not import_result["passed"]:
                failed = True
                print("import pass FAILED; checks will not run")
        if import_result is None or import_result["passed"]:
            for check in checks:
                result = run_check(
                    args.godot, project_dir, check,
                    os.path.join(logs_dir, f"check-{check['name']}.log"),
                    os.path.join(logs_dir,
                                 f"engine-check-{check['name']}.log"))
                results.append(result)
                status = "PASS" if result["passed"] else "FAIL"
                detail = "" if result["passed"] else (
                    " (" + ", ".join(result["reasons"]) + ")")
                print(f"  {check['name']}: {status}{detail}")
                if not result["passed"]:
                    failed = True
        else:
            for check in checks:
                results.append({"name": check["name"], "passed": False,
                                "reasons": ["skipped: import failed"],
                                "skipped": True})

    finished = datetime.datetime.now(datetime.timezone.utc).isoformat()
    report = {
        "version": RUNNER_VERSION,
        "run_dir": run_dir,
        "project": project_dir,
        "manifest": manifest_path,
        "godot": args.godot,
        "engine_version": probe.get("version"),
        "engine_probe": probe,
        "filter": args.filter,
        "default_timeout": default_timeout,
        "skip_import": args.skip_import,
        "started_at": started,
        "finished_at": finished,
        "import": import_result,
        "checks": results,
        "summary": {
            "selected": len(results),
            "passed": sum(1 for r in results if r.get("passed")),
            "failed": sum(1 for r in results if not r.get("passed")),
        },
    }
    try:
        with open(report_path, "w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2)
            handle.write("\n")
    except OSError as exc:
        print(f"error: cannot write report {report_path}: {exc}",
              file=sys.stderr)
        return 1

    summary = report["summary"]
    print(f"{summary['passed']}/{summary['selected']} checks passed; "
          f"report: {report_path}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
