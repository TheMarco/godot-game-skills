# Focused measurement recipes

## Raw timing schema

Save two JSON files using the same exact metric, unit and context:

```json
{
  "metric": "room_construction_cpu",
  "unit": "ms",
  "context": {
    "engine": "record exact godot --version output",
    "platform": "record OS and CPU",
    "renderer": "headless",
    "workload": "seed 7, same ordered 25 cells, warmed"
  },
  "samples": [3.2, 4.1, 3.7, 8.4]
}
```

These illustrative numbers are not benchmarks. Context must describe everything
that materially affects the comparison. Add resolution, quality settings, GPU,
route, actor count and capture duration for a rendered workload. The comparator
can reject mismatched metadata; it cannot detect falsely labeled measurements.

```sh
python3 scripts/compare_timings.py before.json after.json --output comparison.json
```

This command is relative to the installed skill directory. Percentages are
relative changes, with negative values indicating lower cost. A zero baseline
has no meaningful percentage change. The p95 uses nearest-rank selection and
is unstable with small samples; the report flags fewer than 20 samples.

## Construction and streaming

Build the same cells in the same order. Separate cold and warm series. Include
the heavy room style; a mean across empty rooms can hide a furnished outlier.
Track resident nodes/resources alongside per-update costs. Record stages so a
soft 3 ms budget is not reported as a hard cap when one stage takes 12 ms.
Cancellation needs checks during travel, scene teardown and changed generation
inputs. Do not retrieve unfinished asynchronous loads inside the timed loop.

## Navigation

Use blocked routes, narrow openings, moving targets, unreachable targets and
multiple actors. Track per-tick work and time to obtain a usable route. A tiny
tick cost with a search that never completes is not success. Test that actors
continue on collision-safe old routes and adopt replacements from their current
position, instead of snapping back to where a search began.

## Rendering

Capture the same camera trajectory with settling frames for temporal effects.
Record viewport frame time where available, render submission counts and memory.
For GPU changes, measure with a real renderer on the target hardware. Headless
timings cannot establish GPU performance. Occlusion benefits can vary by level:
complex occluders or open spaces can cost more than they save.

Use paired images for fidelity and production motion for temporal behavior.
Disabling TAA or noise can help a diagnostic comparison; disclose that change
and still inspect the normal presentation. Do not ship the diagnostic settings
as a hidden performance improvement.

Official references: [profiling](https://docs.godotengine.org/en/stable/tutorials/scripting/debug/the_profiler.html),
[background loading](https://docs.godotengine.org/en/stable/tutorials/io/background_loading.html),
[occlusion culling](https://docs.godotengine.org/en/stable/tutorials/3d/occlusion_culling.html).
