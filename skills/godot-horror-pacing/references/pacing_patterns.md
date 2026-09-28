# Pacing authority patterns

Read this when designing the arbitration layer or adding a new beat category.

## Authority shape

Keep the authority small: one node (or autoload) holding active leases and
recovery timers, with `try_start_*` gates per category and `end_*` calls that
arm recovery. Systems query before starting; the authority never triggers,
animates, or presents anything itself.

Suggested categories, adapted to your game: hostile encounters, blackouts or
power events, visual/architectural motion, whispers/audio stingers, ambient
touches. Each category gets its own lease timer; one shared recovery timer
paces the overall mix.

## Holds versus recovery

- A **hold** is exclusive presentation ownership (scripted tape, arrival,
  story discovery). Choose whether entering a hold cancels or pauses quiet
  leases. Define active-threat behavior explicitly and release ownership on
  interrupted playback or teardown as well as normal completion.
- **Recovery** is the breath after a beat ends. Denied starts and unseen
  preparations must not arm recovery — only genuine presentations earn it.

## Counting sightings

Count a beat only when its legible motion is visible with a clear line of
sight: preparation frames, offscreen motion, and flat first frames do not
spend cooldowns or quotas. Cancelled or interrupted preparations get a short
retry window, and repeat-delay quotas (per floor, per area) survive
cancellation.

## Deterministic testing

Expose a plain `advance(dt)` clock hook separate from `_physics_process` so a
headless test can step fixed timesteps and assert gate outcomes: denial
during holds, recovery arming on real ends only, quota survival across
cancellation, and lease expiry. Feel and fear still need playtests.
