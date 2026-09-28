# Stage order and comfort pattern

Read this when wiring the presentation nodes or adding a new analog effect.

## Pass order

Decide and document one order, for example: tape-signal degradation, then
tube display, then film grain. Each stage reads the previous stage's output;
reordering is a look change that needs fresh captures. Keep the legacy or
unused branches out of the live path so audits measure what players see.

One proven structure: a shared material factory builds the base preset, a
live-feed variant layers extra wear on top, and in-world screens use the
base preset only. The controller owns transient state (corruption level,
glitch windows, presence) and writes it into material parameters per frame.

## Gameplay-driven damage

Use asymmetric response: fast attack toward rising threat, slow release
toward calm. Typical drivers are nearest-threat proximity (seen or not),
damage events, and scripted bursts of a few frames. The clean tube stays
clean — presence drives the tape material only.

## Comfort and debug

- Keep a list of comfort-relevant uniforms (flicker, slip, loss, dropout,
  tracking error, and similar). The reduced mode scales those down from
  stored raw values; toggling it off restores exactly.
- Provide a presentation gate that suppresses every stage for captures and
  transition tests. This gate must never write to saved preferences —
  assert that separately.
- Register materials for comfort handling at creation so no pass is missed.
