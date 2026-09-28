---
name: godot-performance-workflows
description: Diagnose and improve Godot 4 frame hitches, procedural construction, resource loading, navigation and rendering costs with comparable measurements and behavior-preserving checks. Use for measured performance work; do not lower visual settings without user intent or evidence.
---

# Measure the subsystem before changing it

Find a reproducible slow path and identify its cost before choosing an
optimization. Preserve the user's visual and gameplay targets. A performance
request does not automatically authorize shorter draw distance or fewer enemies.

## Establish comparable evidence

Record engine build, platform/hardware, renderer, resolution, quality settings,
seed, route, warm/cold status, measured subsystem and sample count. Separate
import time, first load, warmed construction, streaming CPU work, simulation,
renderer submission and GPU frame time. A missing GPU timer means unavailable.

Use the same workload before and after, with representative repeated runs.
Profile in isolation; simultaneous imports, audits and benchmarks contaminate
timing. A narrow subsystem benchmark cannot support a whole-game FPS claim.
Read [measurement recipes](references/measurement.md) when selecting fixtures.

## Choose an intervention supported by the bottleneck

| Evidence | Candidate change | Required preservation check |
| --- | --- | --- |
| Repeated identical construction | Exact-input resource/metadata cache | Same geometry, materials, ownership and bounded cache lifetime |
| Large streaming spikes | Off-tree stages with a soft work budget | Cancellation, arrivals, collision and interaction state |
| Blocking first-use loading | Request resources early; poll readiness | No premature retrieval or consumed encounter before readiness |
| Navigation spike or starvation | Incremental bounded search and retained safe route | Collision, moving targets, handover and unreachable retry |
| Many hidden submissions | Selective opaque occlusion or suitable batching | Openings, transparent surfaces, shadows and camera/photo views |
| Repeated shader work | Algebraically equivalent computation reuse | Paired real-render comparisons and temporal behavior |

Use `ResourceLoader.load_threaded_get_status()` before consuming a request during
active gameplay. `load_threaded_get()` can block while work is unfinished.
Background resource loading does not make arbitrary scene construction or
physics access thread-safe. Inspect the matching engine documentation.

Retain a valid navigation route while a replacement is computed. A moving goal
must not cancel every unfinished search. Bound work by operations as well as a
soft clock budget; an individual physics query cannot be interrupted mid-call.

Do not assume one mesh instance equals one draw call or that fewer draws means
faster rendering. Passes, materials, lights, shadows and culling all matter.
Only use MultiMesh/batching when its visibility and material tradeoffs fit.

## Compare and verify

[compare_timings.py](scripts/compare_timings.py) compares raw sample arrays with
matching metric, units and context. It reports counts, mean, median, p95 and
maximum, and deliberately makes no significance or FPS claim. See the reference
for its input schema. Keep raw before/after evidence and note tradeoffs such as
more resident memory or a higher mean despite fewer spikes.

Run the affected behavioral check and inspect matching rendered frames when
rendering changes. For exact scene fingerprints, pin the engine build. For
pixel comparisons, control temporal history, camera and random noise; also
inspect the normal production effect in motion.

Report where performance improved, where it did not, and what remains
unmeasured. Changes that hide the measured work or alter the workload invalidate
the comparison even when the numbers improve.

Example request: “Use $godot-performance-workflows to diagnose hitches when
entering furnished rooms while preserving the current view distance.”
