---
name: godot-game-verification
description: Run portable Godot 4 headless verification checks from a JSON manifest with bounded sequential execution, log capture, and a JSON report.
---

# Godot Game Verification

Run headless Godot checks deterministically and read the report. Use this
skill when adding or running automated Godot verification (scene audits,
determinism gates, content validation). It needs only a Godot binary, a
project, and a manifest — no other skill, root module, or game-specific
setup.

## Workflow

1. Select the affected checks; run the smallest subset that covers the change
   (`--filter SUBSTRING`). Expand for an affected dependency, failure or
   repository-required gate; do not add an unrelated full sweep to a small edit.
2. Run the import pass once per session (it is on by default); pass
   `--skip-import` only for repeat runs in the same unchanged checkout.
3. Run the runner, then read `metadata/report.json` in the run directory:

```bash
python3 /path/to/installed/godot-game-verification/scripts/run_checks.py \
  --project PATH --manifest checks.json
```

For the manifest schema, log capture rules, and timeout behavior, read
[references/checks.md](references/checks.md).

## Constraints

- Godot errors can exit zero or hang: a check passes only with exit 0, its
  success marker, no `SCRIPT ERROR` / parse / compile / `ERROR:` lines, and
  no leak warnings — inside its timeout.
- Structural assertions (node counts, hashes, invariants) are separate from
  rendered captures (screenshots, video); never judge one by the other.
- Reject empty fixtures: a check that ran zero assertions or produced no
  output is a failure, not a pass.
- Never auto-overwrite a golden baseline; regenerating one is an explicit,
  reviewed step with a diff of what changed.
- Pin the Godot version for structural hashes: digests are comparable only
  between runs of the same engine build (the report records the probed
  version).
