# Construction, state and replacement contracts

## Split data by lifetime

| Data | Owner | Reconstructed from |
| --- | --- | --- |
| Room shape and opening facts | Pure generator | Seed, cell/edge, generator version |
| Mesh/collider nodes | Resident chunk | Facts and authored assets |
| Door angle, collected item | State registry | Semantic ID and saved payload |
| Event timers and actor goals | Runtime system | Explicit run/floor lifecycle |
| Texture/immutable mesh | Resource cache | Asset ID and exact configuration |

Scope caches by all inputs that affect their output. If a cache rounds a color
key but constructs a material from the first caller's unrounded color, build
order changes the result. Either quantize both or use an exact key.

## Canonical boundaries

An east edge of `(x, z)` is the west edge of `(x+1, z)`. Represent both as one
anchor plus an axis, and hash that representation. An edge's logical identity
and which resident cell draws it are separate decisions. If the canonical
owner is unloaded at the visible boundary, retain its boundary geometry or
provide an explicit boundary owner; otherwise edges can vanish.

Use a spanning tree or other connectivity construction when every room must be
reachable. Randomly opening walls is not a connectivity guarantee. Check route
planning against the same openings and collision rules used by the scene.

## Replacement sequence

1. Resolve all affected cells and owning rooms. Validate actor clearances,
   active interactions, and any gameplay witness/visibility requirement.
2. Capture topology and interaction state before changing either.
3. Prepare all replacement nodes without removing installed collision. Budget
   work between stages; one indivisible stage can exceed a soft time allowance.
4. Check every replacement is complete and compatible with required actors.
5. Commit at a safe scene/physics boundary, with dependent processing held.
6. Restore semantic object state, reconnect registrations and retire old nodes.
7. Publish persistence/events and visual feedback only after successful commit.

Handle partial failures explicitly. Do not start irreversible side effects
during preparation. The lab models precommit failure and retained state; a real
game also needs compensation for failures in its own commit-side integrations.

## Focused acceptance cases

- Same facts in forward/reverse construction order and after a revisit.
- Neighbor queries agree at positive and negative coordinates.
- A removed object can return with its old state.
- A failed replacement leaves the old node and collider attached.
- Movement across a boundary and teleport arrival have supporting collision.
- A following enemy retains collision even outside the visible radius.
- Cleanup releases obsolete leases, pending jobs and floor-scoped resources.

The last three require a consumer's actual streaming/actor system. Do not claim
they are covered by the lab's small synchronous example.

Official references: [thread-safe APIs](https://docs.godotengine.org/en/stable/tutorials/performance/thread_safe_apis.html),
[background loading](https://docs.godotengine.org/en/stable/tutorials/io/background_loading.html).
Use the documentation version matching the installed engine.
