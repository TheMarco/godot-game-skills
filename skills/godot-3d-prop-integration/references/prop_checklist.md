# Prop import checklist

Read this when integrating a specific authored prop. Covers the checks worth
running per asset; skip items your project genuinely does not need.

## Before import

- Source location recorded (editable scene + previews), separate from the
  export directory and the runtime import path.
- Real-world units confirmed; pivot at the placement point; front axis
  documented with the asset, not just in chat.
- Use original or appropriately licensed art and record provenance (authored,
  scanned, licensed) per texture. Reference access alone does not grant reuse rights.

## Mesh and material checks

- Triangle and surface counts within the budget you set for this prop class.
- All vertex attributes finite; no zero-area triangles; no unintended
  secondary UV streams.
- Repeated instances share mesh and material resources; per-instance
  variation goes through per-instance uniforms or explicit duplicates.
- LOD or visibility policy decided for large or numerous props.

## Placement and collision

- Footprint, height, and facing verified against measured supports (desk tops,
  aisles, door swings) — not eyeballed in an empty scene.
- Collision is a few grouped primitives matching visible extents; genuine
  openings (wells, entries, ramps, open lids) left passable.
- All four wall/facing orientations exercised where the prop can rotate.
- Old placeholder bodies removed; overlap audit shows no new intersections.

## Behavior and capture

- Animation, interaction callbacks, lights, and shaders from the replaced
  object still work; registration/preload lists updated.
- Studio-style isolated capture plus in-room capture with production
  lighting, reviewed before sign-off.
