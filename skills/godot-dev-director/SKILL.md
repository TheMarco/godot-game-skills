---
name: godot-dev-director
description: Plan and coordinate substantial Godot 4 game development using focused workflows for verification, procedural worlds, performance, props, horror pacing, analog effects, and environment wear. Use for broad builds or changes spanning these areas; use a specialist directly for narrow work.
---

# Godot development director

Turn the requested change into a playable, reviewable result. This pack is
strongest in GDScript and procedural 3D. Adapt to the existing project; do not
convert languages, renderers, scene architecture or test frameworks by default.

## Establish the working contract

1. Read the project's instructions, `project.godot`, relevant scenes/scripts and
   existing checks. Record the installed Godot version and target platform.
2. State the intended behavior and smallest existing check that can verify it.
   For visual changes, identify one representative camera, scene and light setup.
3. Find the ownership boundary: generated data, live scene nodes, persistent
   state, presentation, or tools. Keep unrelated systems out of the change.
4. Build and check one representative case before expanding assets, themes or
   level variants. Preserve a reproducible seed/state when generation is involved.

For an empty project, first establish one working loop and its controls. For an
existing game, extend its architecture and preserve its look and player rules.
Ask only for decisions that materially affect the result and cannot be inferred.

## Select guidance

Load an installed specialist only when it helps the task. Specialists are
optional, not hard dependencies; if missing, inspect the equivalent project
tools and proceed with a focused workflow. Do not assume sibling installation.

| Task | Optional skill |
| --- | --- |
| Imports, runtime checks, captures, regressions | `godot-game-verification` |
| Seeded rooms, streaming, object state, live rebuilds | `godot-procedural-worlds` |
| Hitches, loading, navigation or rendering costs | `godot-performance-workflows` |
| Blender/GLB props, materials, collision, placement | `godot-3d-prop-integration` |
| Coordinating scares, quiet periods and witnessed events | `godot-horror-pacing` |
| VHS/CRT, camera interference and in-world displays | `godot-analog-presentation` |
| Cause-based aging, stains, contact wear and overlays | `godot-environment-wear` |

For 2D, multiplayer, C#, console deployment or a renderer-specific feature,
recognize the pack's limited coverage and consult that project's tools and the
matching official documentation. Do not impose procedural 3D patterns on them.

## Execute proportionately

- Use existing interfaces and tests. Isolate pure decisions from scene effects
  where that makes the requested behavior reproducible.
- Keep gameplay RNG separate from visual/event RNG so cosmetic work cannot
  silently change layouts or encounters.
- Treat loaded Resources as potentially shared. Duplicate mutable per-instance
  materials deliberately; retain reuse for immutable geometry and textures.
- Keep old collision/state valid while replacements are prepared. Report any
  engine/thread restrictions before moving construction to a worker thread.
- If delegation is available and authorized, assign disjoint ownership and a
  concrete deliverable; retain integration and final verification locally.
  The skills do not require delegation, a model, a paid API or an agent host.

## Verify and hand over

Import after adding scripts/assets when the project requires it. Run the
smallest behavioral checks, inspect real rendered output for visual changes,
and exercise movement/transitions for temporal changes. Expand only for an
affected dependency, a failure, or a project-required gate.

Report changed behavior, evidence with paths, and remaining limitations.
Separate source inspection, headless assertions, actual rendering and target
hardware measurements. Passing one category does not establish the others.
Keep evidence outside source assets and leave publishing to an authorized task.

Example request: “Use $godot-dev-director to add a streamed warehouse wing while
preserving saved door states and the current lighting.”
