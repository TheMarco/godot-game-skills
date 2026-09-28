# Contributing

Improve a concrete workflow using a reproducible problem. Keep skills small,
independently installable and useful to an agent that already knows Godot basics.
Place conditional detail in a linked reference and executable helpers inside
the owning skill. Do not require a model, paid service or this source game.

Before changing behavior, identify the smallest relevant check. Run package
validation and affected Python tests; run the Godot lab if its code changes.
Rendered changes need actual images or motion on the stated renderer. Include
engine version, platform and any unverified target in the handoff.

## Evaluate behavior, not prose matching

Use the [evaluation scenarios](docs/EVALUATION.md) in a separate scratch project.
Give the agent the request, relevant skill and raw fixture without the intended
solution. Assess the result and scope preservation; a valid YAML header does
not establish that an agent used the skill well. Record failures and narrow the
correction to demonstrated problems. Do not add a rule for every hypothetical.

## Dependencies and distribution

Python tools use the standard library. New dependencies need a concrete benefit
and installation documentation. Include only original or explicitly compatible
assets, with provenance. Keep generated `.godot` caches, logs, credentials and
large binary captures out of skill installation. Installer tests must use
temporary destinations, never the contributor's actual agent directories.

CI checks Python helpers on Linux. To add a platform/engine compatibility claim,
run its relevant example and error/timeout paths and record the environment in
the validation notes. Do not translate a draw-call reduction into an FPS claim.
