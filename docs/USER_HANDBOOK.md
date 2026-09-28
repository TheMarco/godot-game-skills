# Godot Game Skills user handbook

Use Godot Game Skills to help a coding agent make reliable changes to your Godot
project, or run its small tools directly. Start with one concrete outcome:
retain a door's state, diagnose a hitch, integrate a model, coordinate horror
events, or improve a room's presentation.

This handbook explains the complete shipped package and how to apply it. The
[prompt cookbook](PROMPT_COOKBOOK.md) supplies copyable requests for all eight
skills. The [README](../README.md) is the shorter installation and feature overview.

## Contents

- [What you get](#what-you-get)
- [Install and confirm setup](#install-and-confirm-setup)
- [Choose the right skill](#choose-the-right-skill)
- [Write a useful request](#write-a-useful-request)
- [Your first successful run](#your-first-successful-run)
- [Walkthrough: repair a state-reset bug](#walkthrough-repair-a-state-reset-bug)
- [Walkthrough: diagnose room-entry hitches](#walkthrough-diagnose-room-entry-hitches)
- [Walkthrough: integrate a prop and its wear](#walkthrough-integrate-a-prop-and-its-wear)
- [Walkthrough: coordinate a horror beat and camera effect](#walkthrough-coordinate-a-horror-beat-and-camera-effect)
- [Walkthrough: start a small procedural prototype](#walkthrough-start-a-small-procedural-prototype)
- [Run automated checks in your project](#run-automated-checks-in-your-project)
- [Compare timing measurements](#compare-timing-measurements)
- [Review the results](#review-the-results)
- [Update, restore or remove skills](#update-restore-or-remove-skills)
- [Troubleshooting](#troubleshooting)
- [Frequently asked questions](#frequently-asked-questions)
- [Coverage and further reading](#coverage-and-further-reading)

## What you get

| Part | What it does | Where it runs |
| --- | --- | --- |
| Eight skills | Give an agent task-specific instructions, pitfalls and verification criteria | Your skill-compatible coding agent |
| Skill references | Explain conditional details such as state ownership, effect order or a check manifest | Read by you or the agent as needed |
| Check runner | Imports a Godot project, runs selected scripts with timeouts, and records pass/fail evidence | Python plus an installed Godot executable |
| Timing comparator | Compares raw timing arrays with matching workload metadata | Python |
| Seeded Room Lab | Demonstrates deterministic rooms, retained door state and rejected staged replacements | Godot 4 |
| Installer | Copies selected skills, skips existing copies by default and backs them up on forced update | Python |

Skills guide the agent's work in your project. They do not install gameplay
systems into the editor, inject a runtime into your game, or grant the agent
new tool access. The specialist guidance helps the agent implement and adapt
features; the actual shipped executable examples and tools are listed above.

The package's strongest fit is Godot 4, GDScript and procedural 3D. Existing
projects keep their own architecture, assets, art direction, renderer and test
framework. Plain Python tools need Python 3.10+ and no third-party packages.
Running the game example or engine checks also needs the Godot editor binary.

## Install and confirm setup

### Command conventions

Unless a section says otherwise, run commands from the downloaded or cloned
`godot-game-skills` repository root. Every command below is written on one line to
avoid shell-specific line continuations. Quote paths containing spaces.

`python3` means a Python 3.10+ executable. On a system using `python` or
`py -3` instead, substitute that command after confirming its version.
`godot` means your installed Godot 4 editor executable. A path such as
`/absolute/path/my-game` is an example to replace with your real path.

```sh
python3 --version
godot --version
```

If Godot is outside PATH, the check runner accepts `--godot` followed by its
full executable path. On Windows, use the actual editor executable you
downloaded. On macOS, a `.app` directory itself is not the executable; use the
binary inside its `Contents/MacOS` directory. Check the binary's version first.

### Choose an installation destination

Preview the selected installation before copying:

```sh
python3 scripts/install.py --agent codex --dry-run
```

Install all skills for the agent you use:

```sh
python3 scripts/install.py --agent codex
```

Or choose the Claude destination:

```sh
python3 scripts/install.py --agent claude
```

The installer implements these destinations:

| Option | Destination |
| --- | --- |
| `--agent codex` | `$CODEX_HOME/skills` if configured, otherwise `~/.codex/skills` |
| `--agent claude` | `~/.claude/skills` |
| `--dest DIR` | Exactly the skills directory you supply |

Use the destination actually discovered by your agent. `--dest` is useful for
another compatible host or a project-local skills directory. This package does
not configure that host's discovery paths. Choose either `--agent` or `--dest`.

For a smaller installation, repeat `--skill`:

```sh
python3 scripts/install.py --agent codex --skill godot-procedural-worlds --skill godot-game-verification
```

These are the full valid skill names:

```text
godot-dev-director
godot-game-verification
godot-procedural-worlds
godot-performance-workflows
godot-3d-prop-integration
godot-horror-pacing
godot-analog-presentation
godot-environment-wear
```

### Confirm that the agent can use them

Open your game project in the agent. If necessary, use the host's skill refresh
or start a fresh session. Name a skill explicitly for your first request:

```text
Use godot-procedural-worlds to inspect how this project identifies generated
rooms and retains door state. Identify the relevant files and the smallest
existing regression check. For this request, report findings without edits.
```

A useful response refers to your project's actual files and a relevant workflow.
If the host supports dollar invocation, `$godot-procedural-worlds` is another
way to name the skill. The directory must contain `SKILL.md` directly inside
the skill folder; avoid an accidental extra `skills/skills/` nesting level.

Keep the repository checkout if you want this handbook, contribution guides and
installer. An individual installed skill contains its own instructions and
resources, but the installer does not copy the root handbook into each skill.

## Choose the right skill

Start with one specialist for a narrow request. Use the director when the work
crosses several systems or needs an implementation sequence.

| Skill | Useful inputs | Typical useful result | Evidence to request |
| --- | --- | --- | --- |
| [Development director](../skills/godot-dev-director/SKILL.md) | Feature brief, current scene, constraints and target platform | A scoped implementation integrating the needed systems | One working representative case, then affected checks |
| [Game verification](../skills/godot-game-verification/SKILL.md) | Reproduction, existing tests, seed/state and expected behavior | A reproducible check and honest pass/fail report | Logs, assertions, success marker and exit result |
| [Procedural worlds](../skills/godot-procedural-worlds/SKILL.md) | Generator, streaming code, state lifecycle and seed compatibility | Consistent boundaries and generation, retained state, safe rebuild sequencing | Build-order, revisit, negative-coordinate and failed-staging cases |
| [Performance workflows](../skills/godot-performance-workflows/SKILL.md) | Reproducible slow route, environment and unchanged quality targets | A measured diagnosis and targeted optimization | Comparable samples, tail costs, behavior/fidelity checks |
| [3D prop integration](../skills/godot-3d-prop-integration/SKILL.md) | Model/source files, dimensions, front axis and existing interactions | Correctly placed asset with suitable resource ownership and collision | Isolated and in-game views, collision and interaction checks |
| [Horror pacing](../skills/godot-horror-pacing/SKILL.md) | Event systems, intended priorities and player-facing rules | Coordinated starts, holds, recovery and cancellation | Deterministic gate checks plus ordinary play |
| [Analog presentation](../skills/godot-analog-presentation/SKILL.md) | Desired effect, existing passes, target renderer and comfort settings | Controlled signal/display stages and gameplay feedback | Clean/effected captures, motion and preference checks |
| [Environment wear](../skills/godot-environment-wear/SKILL.md) | Representative surfaces, wear causes and intended intensity | Stable decoration attached to the right geometry | Paired captures, unchanged gameplay collision and bounded cost |

The director can use installed specialists, but it is optional. It can proceed
from the project's own tools if a specialist is unavailable. Installing every
skill does not make every request require every workflow.

## Write a useful request

Give the agent four things: the desired behavior, relevant project context,
constraints to preserve, and a way to recognize success. Use actual scene and
asset paths when you know them. If you do not know the relevant files, describe
how to reproduce the problem and let the agent find the ownership boundary.

```text
Use godot-procedural-worlds to fix doors resetting when I return to a room.
In the warehouse scene, open a door, walk far enough to unload that room,
then return. The door should keep its angle. Preserve the generated layout,
save format and current visuals. Start with one reproducible room and the
smallest relevant check, then review other mutable objects only if the
same mechanism affects them.
```

State intent explicitly when you want a review without edits, or implementation
through verification. For visual work, include a screenshot or reference and
explain what matters: silhouette, scale, atmosphere, readability or motion.
For performance, describe the slow moment and target hardware instead of asking
only for “more FPS.” For generation, include a seed and location when available.

The [cookbook](PROMPT_COOKBOOK.md) covers individual skills and combined workflows.
Its scene names and art requirements are examples to adapt to your game.

## Your first successful run

This walkthrough uses only the shipped example. It gives you a visible result
and a check report before you adapt a workflow to a larger project.

### 1. Open the lab

```sh
godot --path skills/godot-procedural-worlds/assets/seeded-room-lab
```

You should see nine small rooms with orange door panels, a seed label and a
control legend. Geometry is deliberately simple so changes in state and layout
are easy to inspect. The scene is also shown in the README's preview image.

### 2. Exercise the state contract

1. Press `Space` to open the center door.
2. Press `R` to unload and rebuild every room. The center door stays open.
3. Press `M` to remove the door, then `M` again to restore it. Its state survives.
4. Press `F` to simulate a failed staging attempt. The installed room stays.
5. Use left/right arrows to inspect another angle.

The `F` operation demonstrates rejection before replacement is committed. A real
game still needs its own physics synchronization and recovery from failures in
additional registration, interaction or persistence code.

### 3. Run the automated checks

Close the example window and run:

```sh
python3 skills/godot-game-verification/scripts/run_checks.py --project skills/godot-procedural-worlds/assets/seeded-room-lab --manifest skills/godot-procedural-worlds/assets/seeded-room-lab/checks.json
```

The runner probes the engine, imports the project and runs two checks. Successful
output includes `determinism: PASS`, `state_roundtrip: PASS`, and the report path.
The report and logs live in a fresh directory under the example's
`artifacts/checks/`. A nonzero exit, engine error, timeout or missing success
marker invalidates a check even if other output looks successful.

### 4. Inspect a different seed

```sh
godot --path skills/godot-procedural-worlds/assets/seeded-room-lab -- --seed=31
```

Reusing that seed reproduces its layout. The `--seed` argument is a feature of
this example, passed after Godot's `--` separator. Other games need their own
argument handling; installing the skill does not add that flag to them.

### 5. Capture the real render

In a graphical session, replace the output path with an absolute path in an
existing directory:

```sh
godot --path skills/godot-procedural-worlds/assets/seeded-room-lab -- --seed=7 --capture=/absolute/path/lab.png
```

The example waits for rendered frames, saves a PNG and exits. Inspect the image
for visible geometry, readable text and expected framing. Its `--capture` option
also belongs to this example; the headless runner does not capture screenshots.

### 6. Experiment in a copy

Copy the entire `skills/godot-procedural-worlds/assets/seeded-room-lab` folder to
a separate working directory before changing it. Open that copied project with
your agent and ask for one small change, such as a second stateful door. Include
the expectation that existing state and determinism checks continue to pass.

Read the [lab guide](../skills/godot-procedural-worlds/assets/seeded-room-lab/README.md)
for file roles and limits. The lab has no player controller, distance-based
streamer, disk-save system or guaranteed navigation connectivity.

## Walkthrough: repair a state-reset bug

**Goal:** an interaction survives unloading or rebuilding its room.

1. Reproduce the bug in one actual room. Record the seed, location, interaction
   and distance or transition that unloads it. Check whether only streaming
   loses state, or quitting and reopening the game also loses it.
2. Ask `godot-procedural-worlds` to trace the object's identity, state owner,
   capture timing and restoration timing. Keep persistent state separate from
   generated geometry. An instance ID or changing node-name suffix is a warning
   sign when it is used as the durable identity.
3. Implement the narrow correction: stable semantic identity and restoration
   at the appropriate lifecycle point. Preserve records while an object is
   temporarily absent if that is part of the game's behavior.
4. Use `godot-game-verification` to cover interaction → unload → reload. Add
   mutation-away → mutation-back only if the game has that lifecycle.
5. Revisit the room in normal play. Check the visual pose and collision agree.

**Expected handoff:** the affected files, a reproducible case, the state's
lifetime and the check result. Keeping state through streaming does not
establish saving across application restarts; request that separately when needed.

The lab's [state-round-trip check](../skills/godot-procedural-worlds/assets/seeded-room-lab/checks/state_roundtrip.gd)
is a concrete example. Adapt the contract to your object's API rather than
introducing a second state system beside the one your game already owns.

## Walkthrough: diagnose room-entry hitches

**Goal:** reduce a reproducible hitch while keeping the requested quality.

1. Pick a short repeatable route through the slow room. Record the engine,
   hardware, renderer, resolution, seed and quality settings.
2. Ask `godot-performance-workflows` to identify what spikes: first resource
   load, object construction, navigation, script work or rendering. Measure
   cold and warmed behavior separately.
3. Make one intervention supported by the measurements. Examples include an
   exact-input cache, staged construction or a readiness-checked resource load.
   Changing view distance, enemy count or artwork is a separate design decision.
4. Repeat the same workload. Compare mean, p95 and maximum as well as any
   memory/residency tradeoff. The [timing tool](#compare-timing-measurements)
   summarizes samples that you or the agent collect.
5. Run the affected gameplay check and inspect corresponding frames when
   appearance could change. Include an arrival or revisit if streaming changed.

**Expected handoff:** what was measured, what changed, where the result improved
or regressed, and what remains unmeasured. Reduced construction time or draw
counts alone cannot establish whole-game FPS or performance on other hardware.

## Walkthrough: integrate a prop and its wear

**Goal:** replace a placeholder with an authored model that works in its room.

1. Supply the GLB and, when available, its editable source. Describe intended
   dimensions, pivot, front direction and the behavior of the current prop.
2. Use `godot-3d-prop-integration` on one representative placement. Inspect it
   at gameplay distance under actual room lighting before expanding the family.
3. Check collision and retained behavior. A kiosk's staff opening should stay
   open; a desk should support its objects; a replaced interactive screen should
   keep its callbacks. Remove obsolete placeholder bodies.
4. Inspect a second instance before adding individual highlighting or color
   variation. A shared mutable material can accidentally change both instances.
5. If aging is wanted, add `godot-environment-wear`. Tie marks to physical causes,
   attach them to the correct support and choose intensity from your art direction.
6. Move or rotate the furnishing and revisit its room. Wear should follow the
   prop and remain stable; the decorative pass should preserve gameplay collision.
7. Profile repeated placements only if density or measured cost makes it relevant.

**Expected handoff:** asset paths, measured placement, retained interactions,
collision evidence, and isolated plus in-room captures. The package supplies
the integration workflow; you or the agent provide the authored asset and its
appropriate usage rights.

## Walkthrough: coordinate a horror beat and camera effect

**Goal:** introduce an event that fits the game's rhythm and presentation.

1. Describe the event and its relationship to existing threats, scripted scenes
   and quiet moments. Use `godot-horror-pacing` to identify who grants permission
   to start and which system owns the actual event.
2. Define active-event priority, holds, recovery and cancellation. A denied
   attempt is normal. A prepared effect the player never sees should not consume
   a successful-sighting quota; attempt throttling can still prevent busy retries.
3. Exercise interruption and teardown. A cancelled cutscene must not leave a
   permanent hold, and an unloaded room must release its active event ownership.
4. Use `godot-analog-presentation` for an accompanying camera disturbance. Keep
   reactive player-camera state separate from prerecorded media on in-world TVs.
5. Check the effect enabled, disabled and at reduced intensity. Temporary
   diagnostic suppression should preserve the player's saved preferences.
6. Test arbitration with a controllable clock, then play through the event in
   motion using the actual renderer. Visibility, readability and pacing need
   human inspection beyond headless assertions.

**Expected handoff:** the priority/cancellation rules, affected controller and
material ownership, deterministic checks and a motion review. Intensity, timings
and the appropriate amount of quiet remain choices for your game.

## Walkthrough: start a small procedural prototype

**Goal:** establish one working loop before expanding a new game.

Start with `godot-dev-director` and a specific brief: perspective, controls,
one environment, one objective and the visual constraints. For example, a
small warehouse where the player finds a switch and returns to an unlocked exit.
Ask for original simple geometry for the first playable version if no assets
have been supplied.

1. Get the player, interaction and objective working in one room.
2. Add `godot-procedural-worlds` when repeatable generation is needed. Define
   connectivity and room-boundary ownership explicitly; random openings alone
   do not guarantee a path to the objective.
3. Establish stable identities for mutable doors, switches or collected items.
4. Add a representative generated-room check and a real traversal of the loop.
5. Integrate one authored prop or one visual treatment, then inspect it in-game.
6. Expand rooms and asset families after the representative case works.

The lab can teach generation/state contracts; it is not a ready-made first-person
game. Its orbit camera and fixed nine-cell patch would need deliberate replacement
or extension for this prototype. Multiplayer, full save migrations, export
automation and platform certification need their own project-specific work.

## Run automated checks in your project

The [runner reference](../skills/godot-game-verification/references/checks.md)
defines the complete CLI and manifest. The runner invokes check scripts you
provide; it does not discover every test framework or automatically create tests.

### Prepare a meaningful check

Use a focused Godot `SceneTree` script that creates a real fixture, tests an
observable contract, frees its resources and exits. Print a unique success
marker only after the required assertions succeed. Report failure with a
nonzero exit and/or a detected engine error. Reject empty or unbuilt fixtures.

Use the lab's [determinism check](../skills/godot-procedural-worlds/assets/seeded-room-lab/checks/determinism.gd)
and [state check](../skills/godot-procedural-worlds/assets/seeded-room-lab/checks/state_roundtrip.gd)
as examples. They depend on that lab's APIs, so copy them together with the
example project or adapt them to your own scene interfaces. Preserve an existing
test framework when it already handles the requested behavior.

### Describe the check in JSON

This is a complete one-check manifest for the **shipped lab**, where the named
script already exists. Save it to a JSON file if you want to run that subset
separately; the bundled `checks.json` already contains this check and determinism.

```json
{
  "version": 1,
  "checks": [
    {
      "name": "state_roundtrip",
      "script": "res://checks/state_roundtrip.gd",
      "args": [],
      "success_marker": "PASS: state_roundtrip",
      "timeout": 30
    }
  ]
}
```

For your game, point `script` at an existing `.gd` inside that project and use
its real success marker. Names must be unique case-insensitively. Unknown
manifest fields, invalid timeouts and scripts outside the project are rejected.

### Run only what the change needs

From this repository, using your actual project and manifest paths:

```sh
python3 skills/godot-game-verification/scripts/run_checks.py --project "/absolute/path/my-game" --manifest "/absolute/path/my-game/checks.json" --filter door
```

`--filter` matches a substring of check names. Matching no checks is an error.
Use `--godot "/absolute/path/to/godot"` when the binary is not on PATH. Use
`--output "/absolute/path/reports"` to choose a report base directory. Each
invocation creates a fresh child directory there.

If running a separately installed skill, replace the runner's relative path with
the absolute path to its installed `scripts/run_checks.py`. `--project`,
`--manifest` and `--output` resolve from the terminal's current directory;
`res://` script paths resolve inside the Godot project.

The default per-import/check timeout is 60 seconds; a check's manifest timeout
overrides the default for that check. `--timeout 120` changes the default but
does not replace explicit per-check values. The engine version probe has its
own 30-second bound. Use `--skip-import` only when the required import state is
already current; adding assets or scripts may require another import.

### Read the verdict

| Exit | Meaning | Next step |
| --- | --- | --- |
| `0` | Every selected check passed | Review whether the selected checks establish the requested result |
| `1` | Probe, import or a check failed | Read the fresh report and corresponding log; fix the first relevant failure |
| `2` | Invalid configuration or usage | Correct project/manifest paths, fields, filter or arguments |

The report contains engine version, executed commands, timing, marker presence,
errors and per-check results. Full logs preserve details beyond the bounded
error excerpts in the report. A successful marker cannot override a nonzero
exit, error output or timeout. An import failure prevents checks from running.

On POSIX systems the runner terminates its subprocess group on timeout. The
Windows fallback terminates the direct child; descendants may remain. Inspect
the exact owned process if that affects your environment.

## Compare timing measurements

The comparator summarizes measurements supplied by you or an agent. It does
not collect profiling data. First decide the subsystem and workload, then record
matching environment and settings for both series.

The following files are a **synthetic tutorial**, not a performance claim. Save
the first as `before.json` in the repository root:

```json
{
  "metric": "room_build_cpu",
  "unit": "ms",
  "context": {
    "source": "synthetic handbook example",
    "workload": "same five illustrative room builds"
  },
  "samples": [2, 3, 4, 5, 30]
}
```

Save the second as `after.json`:

```json
{
  "metric": "room_build_cpu",
  "unit": "ms",
  "context": {
    "source": "synthetic handbook example",
    "workload": "same five illustrative room builds"
  },
  "samples": [3, 4, 4, 5, 9]
}
```

Run from the repository root:

```sh
python3 skills/godot-performance-workflows/scripts/compare_timings.py before.json after.json --output comparison.json
```

The mean is 8.8 → 5.0 ms and the maximum is 30 → 9 ms, while the median stays
4 ms. With only five samples the nearest-rank p95 equals the maximum, and the
tool warns that the tail estimate is unstable. Lower cost produces a negative
percentage change. A zero baseline produces `null` for percentage change.

The output file must not already exist. Choose a new name for a new comparison;
without `--output`, the JSON is printed without saving a report.

For real measurements, record engine build, hardware/platform, warm/cold state,
seed, route, sample definition and relevant renderer/quality settings. Metric,
unit and the entire context must match exactly; samples must be finite,
nonnegative numbers. Supported units are `ns`, `us`, `ms` and `s`. The tool can
check matching labels, but cannot prove that the underlying workloads matched.

Do not relabel different workloads to make them compare. Collect comparable
data instead. Keep regression or fidelity evidence beside timing evidence;
faster code that changes gameplay may not satisfy the original request.

## Review the results

Ask for evidence proportional to the work:

| Change | Useful evidence | What still needs separate evidence |
| --- | --- | --- |
| Procedural state or topology | Seeded assertions, nonempty scene fingerprints and revisit checks | All possible seeds, long play sessions and disk persistence |
| Props or wear | Collision/interaction checks and actual-room captures | Readability from every camera or performance at untested density |
| Pacing or animation | Deterministic state tests and a played/motion sequence | Player reaction, balance and long-term variety |
| Post-processing | Rendered on/off/comfort comparisons on the stated renderer | Other renderers, GPUs and accessibility preferences |
| Performance | Matched raw samples plus preserved behavior | Whole-game FPS when only a subsystem was measured |

A useful final handoff names the changed behavior, relevant files, checks that
actually ran, and remaining limitations. Source inspection, headless assertions,
rendered output and target-hardware measurements support different conclusions.

If the result misses your intent, give a concrete correction and preserve work
that is already right. “The door state now survives, but its collider stays
closed; inspect that restoration path” is more useful than restarting the whole
feature. The cookbook includes [follow-up prompts](PROMPT_COOKBOOK.md).

## Update, restore or remove skills

The installer copies files; installed skills are not live links to the checkout.
Editing or updating the repository does not automatically update installed copies.

Preview a selected forced update:

```sh
python3 scripts/install.py --agent codex --skill godot-game-verification --force --dry-run
```

Apply it by removing `--dry-run`. Existing selected skills move into a timestamped
folder beneath `.godot-game-skills-backups/` inside the destination before replacement.
The command prints the backup location. A forced install replaces the whole
selected skill folder, so preserve intentional local additions before updating.

To restore a backup, close any task using that skill, move the current skill
folder aside, and copy the saved folder back under the original skill name.
Refresh discovery or begin a new agent session as needed. Backups remain on disk
until you choose to remove them; the installer does not prune them automatically.

To uninstall, remove only the named skill folders you installed. Game-project
changes made with their guidance are separate and remain in your project. There
is no background service or editor plugin to unregister.

## Troubleshooting

| Symptom | Likely explanation | What to do |
| --- | --- | --- |
| Agent cannot find a skill | Wrong discovery path, nested directory or stale session | Confirm the installer destination and `skill-name/SKILL.md`; explicitly name the skill; refresh the host |
| Two versions seem to apply | Duplicate copies in multiple discovery roots | Keep one intended installation per host and move other copies outside its discovery roots |
| Installer prints `SKIP` | Same-named skill already exists | Inspect it, then use a selected `--force` update if replacement is intended |
| Installer refuses a symlink | It protects the existing linked destination | Use a different destination or manage that symlink deliberately yourself |
| Missing Python or unsupported syntax | Python executable is absent or too old | Confirm Python 3.10+ with the exact executable used for commands |
| Engine probe fails | Godot path is missing, unexecutable, timed out or returned invalid output | Run that binary with `--version`; pass its path with `--godot`; inspect `version.log` |
| Import fails before checks | Asset/script import or environment failure | Read `import.log` and fix the first cause; bypassing import does not fix the project |
| `--filter` matches nothing | Filter does not match manifest check names | Inspect the JSON names and use an actual substring |
| Script is rejected | Path is missing, outside the project or not a `.gd` | Use an existing project-contained `res://` path; keep CLI manifest paths separate |
| Check prints PASS but fails | Error output, leak warning, nonzero exit or timeout also occurred | Read the complete fresh log; all pass conditions must hold |
| Check times out | Error path missed `quit()`, a loop hangs, or work exceeds the bound | Inspect the last log entries and termination paths; increase timeout only for justified workload size |
| All checks pass but the scene looks wrong | Headless checks covered behavior, not the render | Inspect a native capture and the affected motion in the actual renderer |
| Lab capture does not appear | Missing parent directory, unavailable graphical session or script error | Use an existing absolute output directory and a graphical run; inspect engine output |
| Screenshot flags do nothing in my game | The flags belong to the lab's script | Add project-specific capture hooks if needed; the runner is headless only |
| Timing comparison rejects context | Environment/workload labels differ | Establish a comparable workload and collect a matching pair |
| Timing output already exists | The tool protects previous reports | Choose a new output filename or print to stdout |
| New art behaves differently across instances | Shared mutable Resource state | Inspect ownership; isolate per-instance changes while retaining appropriate immutable sharing |
| Doors or wear change after returning | Unstable identity, build-order RNG or wrong state lifetime | Reproduce with a fixed seed and inspect capture/restore or decoration inputs |

If a tool is blocked by the host's permissions or runtime environment, record
the exact failed command and error. The skills cannot grant missing permissions,
install a renderer or create unavailable engine capabilities.

## Frequently asked questions

**Can I use this without an AI agent?** Yes. Read the workflows, run the example,
and use the Python tools directly. The skills are plain Markdown with local
resources, not a proprietary runtime.

**Does it work with an existing game?** That is a primary use case. Supply the
relevant scene, problem or feature request. Preserve the existing framework and
architecture unless the task calls for a change.

**Can it help start a game?** Yes, through a scoped development workflow and the
small example. The agent still needs to build your controls, game loop, UI and
other required systems. Start with a representative playable slice.

**Do I need all eight skills?** No. Each specialist can be installed alone. The
director is useful when several areas must work together.

**Do I need paid asset APIs or a particular model?** The package itself requires
neither. Your coding-agent service may have its own requirements. External assets
and generation services are optional choices outside the shipped tools.

**Will it generate finished models, shaders or a full streamer for me?** Those
skills guide an agent's implementation work. There is no bundled asset-generation
API client, production shader library or complete streaming engine. Review the
actual generated code and evidence for your task.

**Does the director require subagents?** No. Delegation depends on the host and
user permissions. The same workflow can run in one agent.

**Can I use it for 2D or C#?** Some verification and measurement practices may
transfer, but the concrete game example and strongest guidance target 3D
GDScript. Adapt deliberately and verify in your own setup.

**Can I use my current test framework?** Yes. Keep useful existing tests. The
runner is an optional interface for focused Godot script checks, not a reason
to replace a working framework.

**Does a passing check mean my game is ready to ship?** It establishes only the
tested contract. Exports, platform behavior, broader playtesting, accessibility
and release requirements need evidence appropriate to your game.

**Can I use the package commercially?** The package is distributed under its
[MIT license](../LICENSE). Review that license and any separate licenses for
assets or dependencies you add to your own project.

## Coverage and further reading

The [validation notes](VALIDATION.md) record actual tested versions and
environments. At initial release, the recorded Godot checks and rendered example
ran on macOS with Godot 4.7.2 and the Compatibility renderer. Other engine/platform
combinations, Forward+, Mobile, C# and exports are unverified here. Consult those
notes rather than treating “Godot 4” as a tested matrix of every version.

The eight workflows originate in procedural 3D development experience, but
agent effectiveness across external games has not been established by a broad
controlled evaluation. [Evaluation scenarios](EVALUATION.md) describe concrete
ways to assess behavior without claiming they already ran everywhere.

- [Prompt cookbook](PROMPT_COOKBOOK.md): ready-to-adapt individual and combined requests.
- [Check manifest and runner reference](../skills/godot-game-verification/references/checks.md): exact CLI, schema and verdict rules.
- [Measurement reference](../skills/godot-performance-workflows/references/measurement.md): comparable construction, navigation and rendering workloads.
- [Construction contract](../skills/godot-procedural-worlds/references/construction.md): ownership, retained state and replacement sequencing.
- [Example project guide](../skills/godot-procedural-worlds/assets/seeded-room-lab/README.md): controls, files, checks and limitations.
- [Contributing](../CONTRIBUTING.md): extending the package and verifying changes.
