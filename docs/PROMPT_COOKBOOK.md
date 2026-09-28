# Godot Game Skills prompt cookbook

Copyable starting requests for the eight agent skills. The agent applies these
workflows to your project; packaged tools and the runnable lab are described in
the [user handbook](USER_HANDBOOK.md).

## Contents

- [How to adapt prompts](#how-to-adapt-prompts)
- [Development director](#development-director)
- [Game verification](#game-verification)
- [Procedural worlds](#procedural-worlds)
- [Performance workflows](#performance-workflows)
- [3D prop integration](#3d-prop-integration)
- [Horror pacing](#horror-pacing)
- [Analog presentation](#analog-presentation)
- [Environment wear](#environment-wear)
- [Combined workflows](#combined-workflows)
- [Reviewing results](#reviewing-results)
- [When checks fail or scope drifts](#when-checks-fail-or-scope-drifts)

## How to adapt prompts

Bracketed names are illustrative examples to adapt, not bundled assets. Replace
them with your scenes, scripts, seeds, and budgets.

- Name one skill, the smallest proving check or scene, and what to preserve.
- Start with evidence for a representative case, then cover affected dependencies
  and preserve any required repository checks.
- New prototypes need a small scope and original simple geometry (boxes,
  planes); this package is not a full starter or streaming engine.

## Development director

Skill: [godot-dev-director](../skills/godot-dev-director/SKILL.md).

```text
Use godot-dev-director to plan a small warehouse-wing prototype in my Godot 4
project. Illustrative scope: three rooms off [rooms/warehouse.tscn], original box
shelving, keep [PlayerController.gd], Compatibility renderer, and current
lighting. Deliver one room and its check first.
```

Expected outcome: staged plan and one implemented room with a relevant check.

```text
Use godot-dev-director to coordinate a change spanning [door_state.gd] and
[room_streaming.gd] so edited doors keep state across unload and rebuild. Preserve
seeds and lighting; verify one edited room first. Report behavior changed,
evidence paths, and limits.
```

Expected outcome: one verified room plus evidence separated by category.

```text
Use godot-dev-director to review my request to add night-shift lighting to
[Floor2.tscn] and tell me which specialist skill fits, what to preserve, and the
smallest representative scene and camera to verify against.
```

Expected outcome: routed recommendation with scope and verification target.

## Game verification

Skill: [godot-game-verification](../skills/godot-game-verification/SKILL.md).

```text
Use godot-game-verification to reproduce the door state bug in
[scenes/TestYard.tscn] (illustrative name): open door, unload, reload, confirm it
stays open. Add one focused check with an explicit success marker. If it exposes
the bug, report the failure accurately; preserve required repository gates.
```

Expected outcome: a regression check that exposes the bug and can verify a later fix.

```text
Use godot-game-verification to run only the checks matching [door] in
[checks.json] (illustrative manifest) via --filter, then read metadata/report.json
in the fresh run directory. Report per-check pass or fail with timeout and error-
line findings.
```

Expected outcome: minimal filtered run with per-check evidence, no full sweep.

```text
Use godot-game-verification to audit my new [puddle_checks.json] (illustrative
name) for empty fixtures: each check must run assertions and emit output. Flag any
that could pass silently and propose a fix. Inspect the referenced check scripts
as well as the manifest. Do not regenerate baselines.
```

Expected outcome: silent-pass risks with concrete script or manifest corrections.

## Procedural worlds

Skill: [godot-procedural-worlds](../skills/godot-procedural-worlds/SKILL.md).

```text
Use godot-procedural-worlds to fix doors resetting when rooms unload in
[room_gen.gd] (illustrative script). Keep the generated map identical for old
seeds. Use semantic door IDs with capture-before-retire and restore-after-build;
verify with edit, unload, reload on one room.
```

Expected outcome: retained door state with map compatibility preserved.

```text
Use godot-procedural-worlds to make shared walls consistent from either neighbor
cell, including negative coordinates, in [grid.gd] (illustrative script). Use
floor division and canonical edges. Check two build orders on a small grid before
wider changes.
```

Expected outcome: matching shared-edge identity across orders and signs.

```text
Use godot-procedural-worlds to add a safe staged rebuild to [WingBuilder]
(illustrative node): prepare off-tree, validate the required set, commit at a
controlled point, and keep old geometry and state on failure. Verify with one
injected staging failure.
```

Expected outcome: staged replacement that retains the installed scene when preparation fails.

## Performance workflows

Skill: [godot-performance-workflows](../skills/godot-performance-workflows/SKILL.md).

```text
Use godot-performance-workflows to diagnose hitches when entering furnished rooms
in [LevelA.tscn] (illustrative scene). Preserve view distance and enemy counts.
First record engine build, renderer, resolution, seed, route, and warm or cold
status, then isolate the slow subsystem before proposing any change.
```

Expected outcome: measured bottleneck statement with comparable context.

```text
Use godot-performance-workflows to compare room-entry samples in [before.json] and
[after.json] (illustrative files) with the packaged compare_timings script. Report
counts, mean, median, p95, and maximum with matching metric and context. State
what improved, what did not, and what remains unmeasured.
```

Expected outcome: honest comparison without whole-game FPS claims.

```text
Use godot-performance-workflows to review my plan to preload [keycard.tscn]
(illustrative scene) before the guard encounter. Require readiness polling before
use so the encounter never consumes an unfinished load. Preserve current behavior
and verify arrival and interaction state.
```

Expected outcome: readiness-checked loading plan with preservation checks.

## 3D prop integration

Skill: [godot-3d-prop-integration](../skills/godot-3d-prop-integration/SKILL.md).

```text
Use godot-3d-prop-integration to replace the break-room cabinet primitive in
[BreakRoom.tscn] (illustrative scene) with my authored GLB [cabinet.glb from
props/cabinet.blend] (illustrative source). Keep its interaction callback and
genuine openings open, use simple grouped colliders, remove the old bodies, and
verify silhouette at the gameplay camera with production lighting.
```

Expected outcome: readable prop that behaves like the replaced object.

```text
Use godot-3d-prop-integration to review why highlighting one kiosk in
[Atrium.tscn] (illustrative scene) recolors every kiosk instance. Check for
shared-material mutation and propose per-instance uniforms or a deliberate
duplicate only where variation is needed.
```

Expected outcome: diagnosis of shared-resource leakage with a minimal fix.

## Horror pacing

Skill: [godot-horror-pacing](../skills/godot-horror-pacing/SKILL.md).

```text
Use godot-horror-pacing to add a ceiling-drip ambient beat that yields to hostiles
and blackouts in [NightShift.tscn] (illustrative scene). Route its start through
the pacing authority as a normal deniable gate, keep behavior in the owning
system, and give major danger longer recovery than whispers. Verify with a
deterministic clock test plus a short play session.
```

Expected outcome: beat that never talks over higher-priority danger.

```text
Use godot-horror-pacing to check why scripted tapes in [TapeRoom.tscn]
(illustrative scene) get talked over by whisper stingers. Define which leases
pause, cancel, or continue during the hold, and release the hold on completion,
interruption, and teardown. Check the hold transitions with a controllable clock.
If randomized retries are involved, keep their RNG separate from world generation.
```

Expected outcome: hold design with verified entry and exit behavior.

## Analog presentation

Skill: [godot-analog-presentation](../skills/godot-analog-presentation/SKILL.md).

```text
Use godot-analog-presentation to add a mild damage-driven tracking burst to the
player-camera feed in [Camcorder.tscn] (illustrative scene). Keep signal and
display as independent stages with a documented pass order, drive corruption from
the controller with fast attack and slow release, and verify API names against my
engine version. Provide a reduced-intensity path and a clean-debug view that
preserves saved preferences.
```

Expected outcome: reactive damage that looks deliberate and stays optional.

```text
Use godot-analog-presentation to review why the pause menu in [HUD.tscn]
(illustrative scene) still flickers when the VHS stage is disabled. Check for
shared materials leaking live-feed wear and for debug suppression rewriting
preferences. Verify with on, off, and reduced-comfort captures on the target
renderer.
```

Expected outcome: stage-separation fix verified by three paired captures.

## Environment wear

Skill: [godot-environment-wear](../skills/godot-environment-wear/SKILL.md).

```text
Use godot-environment-wear to add restrained traffic wear to the corridor carpet
in [HotelWing.tscn] (illustrative scene). Name a physical cause for each mark,
seed from stable position plus room identity, and leave collision, navigation,
lighting, and interactions unchanged. Validate one room with paired wear-on and
wear-off captures first.
```

Expected outcome: subtle cause-based aging proven not to alter gameplay.

```text
Use godot-environment-wear to check why scuff marks in [Lobby.tscn] (illustrative
scene) move after streaming out and back. Check for seeds from instance IDs or
build order, attach patches to supporting meshes, and cap overlay counts per chunk
with sparse small transparents.
```

Expected outcome: stable wear that follows its support within budget.

## Combined workflows

Chain skills in one request. Adapt names and scope.

```text
Use godot-dev-director with godot-procedural-worlds and godot-game-verification to
add a warehouse wing prototype to my Godot 4 project. Illustrative scope: two
rooms off [Dock.tscn], original box racks, semantic door IDs, one representative
room first. Preserve lighting and saved states; verify with one filtered check
plus a walk through the new boundary.
```

Expected outcome: one room proving generation, state, and checks together.

```text
Use godot-dev-director with godot-horror-pacing and godot-analog-presentation to
stage a short horror beat in [WardB.tscn] (illustrative scene): a yielded ambient
drip, one scripted tape hold with clean release, and mild camera corruption with
attack and release plus a reduced-intensity path. Preserve pause and menu states;
verify logic with a clock test and feel with a short play session on the target
renderer.
```

Expected outcome: paced beat with readable presentation and comfort path.

```text
Use godot-dev-director with godot-3d-prop-integration, godot-environment-wear, and
godot-performance-workflows to place an authored reception desk in [Lobby.tscn]
(illustrative scene) with cause-based scuffs that move with the desk. Preserve
interactions and collision coverage, prefer opaque variation over decal stacks,
and measure one subsystem before and after.
```

Expected outcome: integrated hero prop with stable attached wear and measured cost.

## Reviewing results

After any change, ask for a scope-and-evidence review: what was preserved, the
smallest verified case, and headless assertions separated from rendered proof.
Identify unrelated changes without reverting another contributor's work. For
visual work, ask for appropriate captures under real level lighting; add
headless evidence when a behavior or structural invariant needs checking.

## When checks fail or scope drifts

```text
The filtered check [door_state_roundtrip] (illustrative name) fails after my edit
to [door_state.gd]. Reproduce it headlessly, report exit code, success marker,
error lines, and timeout separately, and propose the smallest fix that preserves
old seeds. Start with the affected check and preserve required repository gates.
```

Expected outcome: isolated failure diagnosis with a minimal fix.

```text
My request grew from one room to five variants before anything was verified.
Reduce it to the smallest case in [WingA.tscn] (illustrative scene), name what to
preserve, and define the one check or paired capture that must pass before
expanding.
```

Expected outcome: rescoped task with one clear exit criterion.
