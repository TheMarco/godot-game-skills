# Behavioral evaluation scenarios

These are reproducible review prompts and acceptance criteria, not claims that
an evaluation has already run. Use a scratch project and preserve the user's
constraints. Keep the answer criteria from the agent performing the exercise.

| Skill | Request / fixture | Observe |
| --- | --- | --- |
| Director | Add a warehouse variant to an existing lit room without changing the renderer. | Inspects existing boundaries; completes one representative room first; verifies proportionately. |
| Verification | A check prints its PASS marker then emits SCRIPT ERROR and exits zero. | Runner fails. A second run in the same output base cannot reuse the first marker. |
| Procedural worlds | Open the center door, remove its room, rebuild in reverse order. | Geometry repeats and door state survives. Failure injection keeps the installed room. |
| Performance | Mean improves but p95 worsens under the same workload. | Reports both; does not claim universal speedup or infer FPS from subsystem time. |
| Props | Two kiosks share one material; highlight only one and retain a passable staff opening. | Resource isolation only where needed; correct collision; actual room inspection. |
| Horror | A prepared visual event is cancelled before the player sees it. | Does not consume a successful-sighting quota; short retries do not starve higher-priority beats. |
| Analog | Add a damage burst without affecting prerecorded in-world video. | Distinct mutable materials, stage order, comfort handling, real-render comparison. |
| Wear | Add traffic scuffs to furniture that can move and unload. | Stable marks follow support; physics and interactions stay unchanged; bounded overlay cost. |

For skill-quality experiments, compare observable outcomes with and without the
skill using the same task, engine, fixture and model settings. Record defects,
unnecessary scope changes, missing evidence and remaining manual work. Do not
equate longer instructions, smaller output, or passing metadata validation with
better game-development results.
