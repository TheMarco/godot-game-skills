---
name: godot-analog-presentation
description: Build and debug Godot 4 VHS/CRT presentation with separate signal and display stages, reactive camera effects, distinct in-world screen materials and comfort controls. Use for analog camera or television rendering.
---

# Godot Analog Presentation

Add tape/VHS-style presentation to a Godot 4 game: signal degradation (noise,
tracking, dropouts, chroma error) as one stage, display emulation (tube,
grain) as a separate stage. Apply the same separation to in-world displays when
needed; prerecorded content can retain its own presentation preset.

## Workflow

1. **Separate signal from display.** Degrade the recorded signal first, then
   display that result on an emulated tube. Either stage can be toggled
   independently, and the display stage must also accept a clean image.
2. **Order effects deliberately.** Document your pass order (e.g. tape signal,
   then tube display, then grain). Changing order changes the look; treat it
   as an authored choice, not plumbing.
3. **Distinguish live feed from in-world media.** The player-camera feed may
   carry extra wear and reactive damage; recordings shown on in-world screens
   keep their own preset. Share a base material factory, then layer live-only
   wear on top — never the reverse.
4. **Drive damage from gameplay with attack and release.** Threat proximity or
   events raise corruption fast and let it settle slowly, so footage breaks
   before the cause is visible and recovers after it is gone. Keep the
   corruption value in the controller, not in the shader.
5. **Protect comfort and accessibility.** Provide a reduced-intensity path that
   lowers flicker, slip, and loss effects, and a temporary clean-debug view
   that suppresses all presentation without changing saved preferences.
6. **Check the real renderer.** Screen-reading shaders behave differently per
   renderer. Consult the official docs for your engine version — the
   [screen-reading shaders](https://docs.godotengine.org/en/stable/tutorials/shaders/screen-reading_shaders.html)
   for screen texture sampling, the
   [Viewport docs](https://docs.godotengine.org/en/stable/classes/class_viewport.html)
   and [BackBufferCopy docs](https://docs.godotengine.org/en/stable/classes/class_backbuffercopy.html)
   for capture nodes — and verify API names against your version rather than
   trusting remembered calls.

For pass-ordering notes and a comfort-field pattern, read
[references/stage_order.md](references/stage_order.md).

## Adaptation criteria

Preset values, damage intensity, attack/release rates, and which effects exist
at all are art direction — tune them against your own scenes and target
hardware. Effect sample counts are not GPU time estimates; measure on device.

## Common failures

- Reading the screen buffer with a call that does not exist in the project's
  engine version — always verify against versioned docs.
- One-frame exposure lag from sampling a stale copy after the source changed.
- Debug suppression that silently rewrites the player's saved preferences.
- Live-feed damage leaking onto in-world recordings via a shared material.
- Judging the look from headless or thumbnail captures instead of the real
  display path at full frame rate.

## Verification

- Headless runs can assert controller state (holds, corruption curves,
  preference preservation) but cannot show the look. Graphical captures must
  run on the target renderer with production settings.
- Compare captures with presentation on, off, and in reduced-comfort mode;
  confirm the off state leaves saved preferences untouched.

## Example invocations

- "Use $godot-analog-presentation to add a mild tracking-error burst when the
  player takes damage."
- "Use $godot-analog-presentation to review why the pause menu still flickers
  when the VHS stage is disabled."
