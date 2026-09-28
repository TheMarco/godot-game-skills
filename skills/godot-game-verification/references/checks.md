# Checks reference: manifest, capture, and run practices

Read this when writing a manifest, adding a check script, or interpreting a
run report. Contents: manifest schema, CLI, pass/fail rules, log capture,
timeouts, output layout, golden baselines.

## Manifest schema (version 1)

JSON object with exactly these fields:

```json
{
  "version": 1,
  "checks": [
    {"name": "determinism", "script": "res://checks/determinism.gd",
     "args": [], "success_marker": "PASS: determinism", "timeout": 30}
  ]
}
```

- `version`: must be the exact JSON integer `1` (`1.0` is rejected).
- `checks`: nonempty list. Unknown fields anywhere are rejected.
- `name`: unique case-insensitively (portable filesystems), and a safe
  file basename (letter/digit start; then letters, digits, `.`, `_`,
  `-`). Names like `version` or `import` are allowed: check logs are
  prefixed with `check-`, so they cannot collide with invocation logs
  (and `check-CON.log` avoids Windows reserved device names).
- `script`: a `res://` path to an existing `.gd` file strictly inside the
  project (no `..` escape). Passed to Godot as an absolute path.
- `args`: list of strings, passed after `--` (default `[]`).
- `success_marker`: single-line string with non-whitespace content that
  must appear in the check's combined output. Each check needs its own
  marker.
- `timeout`: per-check seconds, a finite positive number, never a boolean
  (default: the CLI `--timeout`, itself defaulting to 60).

CLI paths (`--project`, `--manifest`, `--output`) resolve relative to the
caller's working directory. `--godot` defaults to `$GODOT`, then `godot`.

## CLI

```bash
python3 scripts/run_checks.py --project PATH --manifest PATH \
  [--godot PATH] [--filter SUBSTRING] [--timeout SECONDS] \
  [--skip-import] [--output DIR]
```

Exit codes: `0` all selected checks passed; `1` a check, the import
pass, or the engine probe failed; `2` usage, project, manifest, or filter
error (including a filter that matches nothing).

A failed, timed-out, or empty engine probe (`godot --version`) fails the
whole run: import and checks are skipped, but a report is still written.
A missing or unexecutable binary is reported the same way, without a
traceback.

## Pass/fail rules

A check passes only if **all** hold:

1. Exit code 0 within its timeout (a hang is killed and fails).
2. Its `success_marker` appears in the combined output.
3. The full log contains none of: `SCRIPT ERROR`, `Parse Error`,
   `Compile Error`, a line starting with `ERROR:`, or leak warnings
   (`ObjectDB instances leaked`, `resources still in use at exit`).

Rule 3 applies even when the exit code is 0 and the marker is present:
Godot scripts can print errors and still exit cleanly. There are no global
suppressions; if a check legitimately emits one of these lines, change the
check to not emit it rather than filtering the runner.

The import pass (`godot --headless --path PROJECT --import`, run once
unless `--skip-import`) needs no marker, but any error output, nonzero
exit, or timeout fails the run and prevents all checks from running.

## Log capture

- Every invocation's combined stdout/stderr streams directly to its own
  log file (never buffered unbounded in memory), plus a `--log-file`
  engine log. Checks use `logs/check-<name>.log` and
  `logs/engine-check-<name>.log`; the probe and import
  pass use `logs/version.log` and `logs/import.log`.
- Before error matching, each line is normalized: ANSI color sequences
  are stripped and leading whitespace is removed, so a real engine
  `ERROR:` cannot evade detection behind coloring or indentation.
- The engine version is probed once (`godot --version`, 30 s bound) and
  recorded in the report; structural hashes are only comparable between
  runs with the same probed version.
- `metadata/report.json` records per invocation: argv, elapsed seconds,
  exit status, timeout flag, matched marker, and error lines (first 20 in
  the report; full text stays in the log files).

## Timeouts

Every subprocess is bounded, including the version probe and the import
pass. On POSIX each child runs in its own process session and the whole
group is signalled on timeout, so stray grandchildren cannot linger. On
Windows the runner falls back to terminating the direct child; grandchildren
may survive a timeout there. An interrupt (`KeyboardInterrupt`,
`SystemExit`) during a wait terminates the owned child (or group) before
propagating. The runner never kills unrelated processes and never uses
shell interpolation (argv lists only).

## Output layout

`--output DIR` names a base directory, never the run dir itself: every run
creates a fresh unique child (`<UTC stamp>-pid<PID>`, suffixed while it
exists), so stale logs or markers can never leak from an earlier run into a
later verdict. The default base is `project/artifacts/checks/`. Existing
output is never deleted.

```text
<base>/<run-id>/
|-- metadata/report.json
`-- logs/
    |-- version.log
    |-- import.log (+ import-godot.log)
    `-- check-<name>.log (+ engine-check-<name>.log)
```

## Check scripts and golden baselines

- Keep check scripts small `SceneTree` scripts with explicit assertions and
  one final marker print, e.g. `print("PASS: determinism")`.
- A check that runs zero assertions or emits nothing fails review: reject
  empty fixtures rather than marking them passed.
- Keep structural assertions (hashes, counts, invariants) separate from
  rendered captures (screenshots, video frames); a pixel diff never proves
  a structural invariant and vice versa.
- Never auto-overwrite a golden baseline file. Regenerate only on explicit
  request, and diff old vs new so the change is reviewed.
