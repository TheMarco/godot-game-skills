---
name: godot-procedural-worlds
description: Build and modify seeded procedural Godot 4 worlds with consistent shared edges, load-order-independent generation, streamed object state, and safe scene replacement. Use for room/chunk generators and runtime rebuilds, not as a universal architecture for authored levels.
---

# Procedural worlds that survive rebuilding

Make the same seed and coordinates reproduce the same generated facts. Keep
player-driven changes separate so unloading a room does not reset its objects.
Preserve an existing generator's compatibility contract unless the task changes it.

## Inspect the boundaries

Identify seed derivation, cell dimensions, edge ownership, room anchors,
construction order, state ownership, streaming triggers and collision consumers.
Record whether old saves/seeds must survive the change. A canonical edge must
have the same identity when queried from either adjacent cell, including at
negative coordinates. Use floor division for world-to-cell conversion.

## Build stable generation

- Derive local decisions from `(world seed, coordinates, stable domain/salt)`.
  A shared sequential RNG makes results depend on build order unless carefully
  partitioned. Keep decoration and encounter streams independent.
- Treat domain IDs and seed derivation as versioned data. Removing a theme must
  not renumber the remaining IDs when old seeds need to reproduce.
- Assign shared walls to canonical edges and multi-cell furniture to one room
  owner. Residency must include the owner while a dependent member is needed.
- Pass construction facts into builders and expose a narrow scene-writing
  interface where useful. Do not force this abstraction into a tiny generator.
- Never use instance IDs, generated node-name suffixes or time for stable keys.

## Retain mutable state

Give each interactive generated object a semantic ID such as
`cell:-2:5/door:east`. Store only explicit, versioned values: open angle,
collected status, switches. Do not serialize live node references or use paths
whose sibling numbering changes after a rebuild.

Capture before retirement, restore after construction, and keep the state record
while the object is temporarily absent. Define floor/run/save lifetimes instead
of silently retaining everything forever. A streamed state registry is not a
disk-save implementation; separately handle atomic save writes and migrations
if the user asks for persistence across application restarts.

## Stream and replace safely

Separate visual visibility from required collision residency. Players, pursuing
actors and transitions may need collision beyond the camera's visible cells.
Prepare a replacement off-tree, validate its complete required set, then commit
at a controlled synchronization point with gameplay processing held as needed.
Off-tree work is not automatically thread-safe. Keep physics queries and live
scene changes on their appropriate engine thread.

If preparation fails, preserve the installed geometry, state and topology.
Rollback must restore the exact previous state, including topology history and
interaction ownership. A fade or blackout alone does not make a swap safe.
Read [the construction contract](references/construction.md) for the transaction
sequence and cases worth checking.

## Start with the portable example

[Seeded Room Lab](assets/seeded-room-lab/README.md) is a small Godot project with
pure cell facts, canonical edges, stateful doors, a staged rebuild, deterministic
checks and a real-render capture path. It uses original box geometry and no
external assets. Copy the folder to a scratch workspace before experimentation.
It demonstrates the contracts; it is not a complete streaming engine or player
controller. Keep the consumer project's existing generator when adapting it.

## Verify the changed contract

Use two build orders and include negative coordinates and shared boundaries.
Exercise edit → unload → reload and mutation-away → mutation-back. Inject a
failed staging attempt and verify old collision and state remain installed.
Check nonempty geometry before trusting hashes. Pin the Godot build for scene
fingerprints and inspect intended baseline differences before accepting them.

For a live integration, walk through boundaries, revisit edited objects, follow
a transition and verify arrival support in the actual game. Example assertions
cannot establish that every procedural seed is navigable.

Example request: “Use $godot-procedural-worlds to fix doors resetting when chunks
unload, without changing the generated map.”
