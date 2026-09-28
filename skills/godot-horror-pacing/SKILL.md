---
name: godot-horror-pacing
description: Coordinate Godot 4 horror encounters, ambient events and scripted presentations with shared priorities, recovery and witnessed-event tracking. Use when beats overlap, starve one another, or consume cooldowns before the player sees them.
---

# Godot Horror Pacing

Coordinate scare and atmosphere systems (hostiles, blackouts, visual beats,
whispers, ambient stingers) so unrelated beats never talk over each other and
the player gets a breath after major danger. Use when adding or tuning a
horror beat — not for general game feel or difficulty balance.

## Workflow

1. **Keep behavior in the owning system.** Each horror system owns its
   geometry, probability, and presentation. The pacing authority only answers
   "may this start now?" and tracks active leases plus recovery time.
2. **Arbitrate starts, not content.** Offer `try_start_*` style gates per beat
   category; a denied start is a normal outcome the owner handles (retry
   later, stay dormant), never an error.
3. **Hold scripted presentations.** A tape, card, or arrival sequence owns the
   mix according to the game's rules. Define which leases pause, cancel or
   continue, and what happens to active threats. Release the hold on completion,
   interruption and teardown; quiet starts must respect the chosen ownership.
4. **Recover proportionally.** After a beat ends, block fresh optional beats
   for a recovery window. Major danger earns a longer breath than a whisper;
   tune each window to your game's rhythm.
5. **Spend sightings only on witnessed beats.** Count a beat as "seen" only
   when its legible motion is actually visible to the player. Unseen,
   cancelled, or interrupted preparations should not consume a successful-sighting
   quota. Keep attempt throttling separate so short retries cannot run unbounded.
6. **Seed randomness per system.** Each director uses its own seeded RNG so
   pacing stays reproducible and one system never drains another's stream.
   World-generation randomness is separate.

For authority shape, hold/recovery patterns, and deterministic clock testing,
read [references/pacing_patterns.md](references/pacing_patterns.md).

## Adaptation criteria

Recovery lengths, cooldowns, reveal quotas, and which beats outrank others are
your game's horror rules — derive them from playtesting your own mix, not from
another project's constants. A slow-burn exploration game and a chase-heavy
game need different windows.

## Safety and player agency

Eligibility gates may delay any beat; the pacing layer must never force an
event the safety check rejects (unsafe geometry, mid-interaction, paused or
menu states). For discovery-driven events, combine timing with where the player
walks and looks. Authored deadlines and unavoidable events remain design choices.

## Common failures

- Recovery applied on denied starts, starving the mix after nothing happened.
- A cancelled preparation consuming a reveal quota or long cooldown.
- Shared-global RNG making beats irreproducible and order-dependent.
- Scripted holds that forget to release, silencing the game indefinitely.
- New beat added without routing its start through the authority.

## Verification

- A deterministic clock test (advance fixed timesteps, assert gate outcomes)
   proves arbitration logic headlessly. It proves nothing about fear, timing
   feel, or visibility — those need ordinary play sessions.
- Playtest with the authority disabled versus enabled: denial paths, hold
   entry/exit, and the first minute of a floor (arrival grace vs. early beats).

## Example invocations

- "Use $godot-horror-pacing to add a ceiling-drip ambient beat that yields to
  hostiles and blackouts."
- "Use $godot-horror-pacing to check why scripted tapes keep getting talked
  over by whisper stingers."
