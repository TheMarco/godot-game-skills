# Extraction notes

The source project is Liminal, a Godot procedural 3D horror game. This package
extracts decision criteria and failure lessons, with newly written small helper
tools and a minimal scene. It does not export the game's implementation wholesale.

| Skill | Source knowledge | Generalization |
| --- | --- | --- |
| Verification | Audit runner and generated-world fingerprints | Manifest-driven subprocess runner, explicit markers, timeouts and fresh reports |
| Procedural worlds | Pure world queries, chunk/runtime-state and mutation boundaries | Original nine-cell example, stable IDs, absent-object state, staged rejection |
| Performance | Construction, streaming, renderer and navigation measurements | Context-matched samples, subsystem attribution, bounded work and fidelity checks |
| Props | Blender replacements and real-room inspections | Asset ownership, units/pivots, collision openings, retained behavior |
| Horror | Shared pacing and witnessed architectural events | Configurable priorities, holds, recovery and cancelled preparations |
| Analog | Independent signal/display controllers and paired render checks | Composable effects, distinct materials, preference-preserving diagnostic views |
| Wear | Physically motivated, deterministic decoration | Cause-based placement, attachment, budgets and gameplay invariants |

Liminal's world dimensions, theme IDs, art direction, event timings, private
paths, platform-specific error exceptions and historic benchmark numbers are
not defaults here. The scene uses original geometric primitives. No external
assets or source-game narrative are needed to use the package.

The Three.js Game Skills repository inspired packaging specialist instructions
with self-contained resources. This package is independently authored; its
support and performance claims apply only to evidence recorded here.
