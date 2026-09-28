---
name: godot-environment-wear
description: Add or debug deterministic decorative wear in Godot 4 environments, with cause-based placement, attachment to moving props, bounded overlay cost and unchanged gameplay collision. Use for scuffs, stains, deposits and aging passes.
---

# Godot Environment Wear

Add aging (scuffs, stains, deposits, paint ghosts) according to the requested art
direction. For a decorative-only task, the wear pass must not
alter collision, navigation, lighting, labels, or interactions. Use for
post-placement aging — not for base texturing or destruction systems.

## Workflow

1. **Follow physical causes.** Every mark needs a plausible cause: contact,
   plumbing, fixtures, traffic, prior damage, or maintenance. If you cannot
   name the cause, cut the mark.
2. **Seed from stable local identity.** Derive placement and variation from
   physical position plus district/room identity — never from instance IDs,
   build order, or time — so wear is identical across streaming and revisits.
3. **Attach wear to its support.** Surface patches parent to their supporting
   mesh; prop wear uses the prop's own triangles. Moving or rotating a
   furnishing carries its wear with it.
4. **Budget tightly per chunk.** Cap patch counts, overlay counts, and special
   cases (lifted edges, rare replacements) per spatial chunk. Ordinary rooms
   should use far fewer than the cap.
5. **Mind transparency and surface cost.** Prefer opaque tint/roughness
   variation over stacked transparent decals. Transparent overlays cost
   fill-rate and sorting; keep them sparse, small, and off emissive or
   gameplay-critical surfaces.
6. **Respect geometry limits.** Keep overlays inside surface bounds, aligned to
   real UVs/grids, offset enough to avoid z-fighting but not so far they
   float. Never alter normals in ways that break lighting reads.

For cause-to-placement patterns and budget guidance, read
[references/wear_patterns.md](references/wear_patterns.md).

## Adaptation criteria

Intensity, tint strengths, patch counts, and which causes appear per district
are artistic choices for the user — not values to copy from another game.
Validate one representative material and room before expanding. Subtle aging
and extensive decay need different coverage and contrast targets.

## Common failures

- Wear shifting between visits because seeds used instance IDs or RNG order.
- Z-fighting or floating decals from offsets tuned on one surface reused on
  all surfaces.
- Transparent overlay stacks harming frame time in large rooms.
- Wear pass accidentally adding colliders, lights, or gameplay objects.
- Emissive screens or readable signage dulled by an overlay that ignored
  material exclusions.

## Verification

- Headless contract checks prove invariants: identical collider graphs and
  gameplay-object counts with wear on versus off, repeated-build stability,
  bounds, strengths, and budgets across seeds and room styles. They do not
  prove the wear looks right.
- Rendered proof needs paired captures under real level lighting: the same
  camera with wear enabled and disabled. Judge subtlety from the pair, and
  review full scenes through the final presentation chain if one exists.

## Example invocations

- "Use $godot-environment-wear to add restrained traffic wear to the hotel
  corridor carpet without touching navigation."
- "Use $godot-environment-wear to check why scuff marks move after the room
  streams out and back in."
