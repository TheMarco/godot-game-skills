# Seeded Room Lab

A small, original Godot 4 contract example. The only art is runtime box
geometry. Open `project.godot` in the editor or run this directory with `godot
--path .`. The engine may create its local `.godot` import cache.

## Try it

- `Space`: toggle the center room's orange door.
- `R`: unload and rebuild all rooms, retaining door state.
- `M`: remove/restore the center door; its state survives absence.
- `F`: fail a staging attempt deliberately; the installed room stays.
- Left/right arrows: orbit the camera.

Use `godot --path . -- --seed=31` for a different repeatable layout.

## Check it

Import once, then run each check with an external timeout or the verification
runner when available. These scripts print one final success marker and exit
nonzero on a failed assertion. Engine error output also invalidates a pass.

```sh
godot --headless --path . --import
godot --headless --path . --script res://checks/determinism.gd
godot --headless --path . --script res://checks/state_roundtrip.gd
```

`checks.json` is compatible with the optional `godot-game-verification` runner.
The project uses explicit `preload` paths rather than depending on a preexisting
global-class cache. For a visual capture, use a real graphical session:

```sh
godot --path . -- --seed=7 --capture=/absolute/path/lab.png
```

The output directory must already exist. The example waits for rendered frames,
saves the viewport and exits. Headless mode is not a substitute for this check.

## What each file demonstrates

| File | Contract |
| --- | --- |
| [world.gd](world.gd) | Pure coordinate/domain decisions and canonical edge queries |
| [room.gd](room.gd) | Facts converted into actual meshes and simple colliders |
| [room_store.gd](room_store.gd) | State keyed by semantic identity, retained during absence |
| [fingerprint.gd](fingerprint.gd) | Explicit fixture-scoped structural fingerprint |
| [determinism.gd](checks/determinism.gd) | Reverse build order, negative coordinates, shared edges, change sensitivity |
| [state_roundtrip.gd](checks/state_roundtrip.gd) | Unload/reload, removal/restoration, failed staging |

The fingerprint includes transforms, box dimensions, color, roughness, collision
size and tree shape. It does not cover arbitrary meshes, shaders, animation,
textures or every physics property. Extend the contract for a consumer's needs,
and compare exact fingerprints only with the same Godot build.

The scene intentionally has no character controller, distance streaming,
background threads, disk saves or navigation guarantee. Shared boundaries are
owned by the lower-coordinate cell, and this fixed patch has an open outer
edge; a production streamer needs explicit boundary residency. The replacement
fixture exercises precommit failure. Real games must synchronize physics and
restore their own registrations if a commit-side integration fails.
