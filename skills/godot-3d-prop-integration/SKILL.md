---
name: godot-3d-prop-integration
description: Import or replace Blender/GLB props in Godot 4 while preserving scale, pivots, material ownership, collision openings and existing interactions. Use for authored furniture, fixtures and hero props.
---

# Godot 3D Prop Integration

Bring an externally authored prop (typically a GLB from Blender) into a Godot 4
scene so it reads well at gameplay distance and behaves like the object it
replaces. Use for hero props, furniture, and fixtures — not for procedural
geometry or character rigs.

## Workflow

1. **Confirm the read first.** Check the silhouette at the actual gameplay
   camera distance and lighting before tuning detail. A prop that only reads
   in a close-up inspector view is not done.
2. **Fix real-world measure.** Model in meters, set the pivot at the placement
   point (usually floor center), and agree on one front axis per prop family
   (e.g. screens face +X). Record footprint, height, and facing with the asset.
3. **Separate source, export, and runtime.** Keep editable sources and
   previews apart from exported GLBs, and import GLBs into scenes rather than
   editing them in place. Re-export must be reproducible from source alone.
4. **Share resources across instances.** Repeated placements share imported
   meshes and materials. Never mutate a shared material per instance — use
   per-instance uniforms or a duplicated material only where variation is
   genuinely needed.
5. **Group collision deliberately.** Use a few simple shapes sized to the
   visible mesh. Leave genuine openings open (staff wells, entries, walkable
   ramps); collision must match what the player sees, including open lids.
6. **Preserve behavior.** If the prop replaces a primitive, carry over
   animation, interaction callbacks, lights, and shaders. Remove the old
   bodies so there are no duplicate colliders.

For the import checklist (budgets, degeneracy, orientation audits), read
[references/prop_checklist.md](references/prop_checklist.md).

## Adaptation criteria

Triangle budgets, surface counts, LOD policy, and front-axis conventions are
project choices — set them from your scene's measured cost, not from another
game's numbers. Small background props need far less than hero pieces the
camera lingers on.

## Common failures

- Buried or floating placement because the pivot is not at the support surface.
- Mirrored or backwards facing from an unrecorded front axis.
- Per-instance material tweaks leaking across all instances via a shared resource.
- Heavyweight collision (concave or per-triangle) where grouped boxes suffice.
- Provenance drift: runtime GLB edited without updating the editable source.
- Reference-photo pixels shipped without appropriate reuse rights or provenance.

## Verification

- Headless checks prove structure only: mesh budgets, finite attributes,
  zero-area triangles, collider coverage, callback wiring, no overlapping
  placements. They say nothing about how the prop looks.
- Rendered proof needs two views: an isolated studio-style capture of the
  prop, and a capture of it in its real room with production lighting. Review
  both before calling the integration done.

## Example invocations

- "Use $godot-3d-prop-integration to replace the break-room vending machine
  primitive with the authored GLB, keeping its interaction."
- "Use $godot-3d-prop-integration to review why these kiosk instances all
  change color when one is highlighted."
