# Wear causes and budgets

Read this when planning which marks appear in a district or room style.

## Cause-to-placement patterns

Tie each mark family to a cause and a support surface:

- Traffic and contact: thresholds, caster zones, hand-height rubs, luggage
  scuffs low on walls (never on high lintels or ceilings).
- Water and plumbing: deposits at fixtures, runoff below equipment pads,
  waterlines and splash residue near water, damp at seams.
- Fixture memory: bolt holes and adhesive ghosts where fittings moved,
  poster and tape ghosts, repaint edges, replacement tiles aligned to grid.
- Maintenance traces: repairs at joints and cable entries, cleaned handles
  amid dust, small lifted finish edges (rare, projecting only millimetres).

Emissive surfaces, readable signage, and gameplay objects are excluded from
overlays. Openings use currently resolved geometry, not stale placements.

## Budget guidance

Set per-chunk caps that fit your scenes — for example separate limits for
surface patches, prop-mesh overlays, fixture-floor groups, and lifted
finishes — and keep ordinary rooms well under them. Cap tint strengths so
most of each finish stays visible, and confine opaque replacements (missing
tiles, mortar patches) to small rare areas aligned to the surface grid.

Run the wear pass once per build after placement and before gameplay
activation. Verify with paired on/off captures under the level's real
lighting, plus a headless invariant check that colliders and gameplay
objects are unchanged.
