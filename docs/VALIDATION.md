# Validation evidence

Initial package validation: September 28, 2026.

## Observed environment

- macOS 27.0, Apple M3 Max.
- Python 3.14.6 for package helpers and tests.
- Godot `4.7.2.stable.official.ed1daf0bf`.
- Real render: Compatibility, OpenGL API 4.1 Metal, 1100 × 720.

## Results

| Check | Result |
| --- | --- |
| Package metadata, self-contained local links and Python syntax | 8 skills passed |
| Standard skill-creator frontmatter validator | 8 skills passed |
| Python helper tests | 53 passed (44 runner; 9 installer/timing) |
| Godot import through packaged runner | Passed, no error lines |
| Real Godot determinism check | Passed: three seeds, reverse construction order, canonical edges, negative coordinates, transform sensitivity |
| Real Godot state check | Passed: unload/rebuild, absent/restored object, rejected staging retaining installed room |
| Native rendered example | Captured and visually inspected; preview in README |
| Isolated installation | Two skills installed separately; example copied to a fresh consumer project; import and both checks passed with spaces in paths |

Runner regression tests exercise zero-exit script errors, missing markers,
timeouts, subprocess-group cleanup on POSIX, import/probe failures, ANSI errors,
fresh output directories and case-insensitive name collisions. Installer tests
use temporary directories and cover default preservation, force-update backup,
dry-run and cache exclusions. Timing tests distinguish mean from tail behavior
and reject incompatible contexts and invalid samples.

PyYAML was used only for the external skill-creator validator in a temporary
development environment. The distributed tools require no third-party Python
packages. The bundled validator intentionally supports this package's simple
single-line metadata schema; it is not a general YAML parser.

## Reproduce

From the repository root:

```sh
python3 scripts/validate_package.py
python3 -m unittest discover -s tests -v
python3 skills/godot-game-verification/scripts/run_checks.py \
  --project skills/godot-procedural-worlds/assets/seeded-room-lab \
  --manifest skills/godot-procedural-worlds/assets/seeded-room-lab/checks.json
```

Each engine run produces fresh logs and `metadata/report.json` beneath the
project's `artifacts/checks/` directory, or beneath the specified `--output`
base. Do not copy a previous run's success markers into new evidence.

For a real render, use the example's `--capture=/absolute/path/lab.png` option
in a graphical session. Inspect that image; a saved file alone does not
establish a correct scene.

## Limits

The Python helpers target 3.10+, but only the observed local version has run
here. The configured Linux CI matrix (3.10/3.12/3.13) has not run on a remote
service yet. Windows and Linux engine runs, other Godot versions, Forward+,
Mobile, C#, exports and target hardware are unverified. Windows timeout
cleanup terminates the direct process; descendants may remain.

The example validates a small contract, not every consumer's scene lifecycle,
streaming behavior, pathfinding or physics synchronization. Specialist prose
was reviewed against source lessons, but a controlled agent-quality evaluation
across external games has not been performed. The evaluation scenarios describe
that next step without claiming it already happened.
