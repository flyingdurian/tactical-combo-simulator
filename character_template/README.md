# Add a character without new combat scripts

Copy `character.tres`, assign a stable character_id/display_name, and fill only supported slots. The normal array is always `[neutral, left, up, down, right]`; two special slots and one ultimate are separate. Empty paths are deliberate unavailable moves, not substitutes. Assign one default assist plus any authored variant paths. The debug UI stages role and assist-variant changes, applied only by Launch new battle.

The package contains portrait and SpriteFrames references, source manifest, native facing, pivot, scale, frame size, hurt rectangle, hurt texture, role support, move availability notes, and optional voice/effect references. Portrait currently reuses an idle-pose asset, not a commissioned portrait. Voice references are empty until actual recordings are mapped. `moves/kosmos.tres` is the filled reference; `PackageValidator.inspect()` checks slots, events, resource existence and pose timing. Missing art visibly falls back and cannot stall the scheduler.

Preserve original sheets and record hashes/dimensions. Crop assembled poses conservatively, preserving costume colors. Put source rectangles, canvas offsets, intended source attack direction and uncertainty in the manifest; do not infer animation order from sheet order. Keep source-facing metadata per pose where weapons or spins change direction. All sprite mirroring is in BattleActor, never negative parent scale plus another flip.

Author one sequence:

1. Inspect anticipation, contact and recovery poses; preserve foot/weapon anchors.
2. Set each pose's duration in ticks, independently of hit events.
3. Define target-relative staging and bounded commitment. A `movement` track is an additional local offset, not a second approach. Do not copy legacy absolute travel into a staged move.
4. Place uniquely named strike intervals at actual visible contact. Supply a small local rectangle or visible projectile origin/speed/lifetime. Eligibility can be any, grounded or airborne.
5. Give each event an explicit reaction, damage, stun/stop and XP. Specials/ultimate category suppresses attack meter gain even if a copied XP field is nonzero.
6. Add sparse effects/sound/camera cues; finish/recover by timeline duration, never `animation_finished` alone.
7. Set chain/cancel windows and projectile-cancel policy. Validate IDs, inspect in MovePreview at full/quarter speed, step every contact, and test both sides and a deliberate miss.

Register the resource path in moves/roster.json. BattleDemo and MovePreview both read this single registry. No actor/controller changes are needed for move behavior within this schema. New behaviors outside supported timeline fields still require an intentional engine extension. Extraction can be assisted; coherent choreography still requires inspection and playtesting.

Optional CharacterSoundProfile: use sounds/reiji.tres as an empty semantic pool example. Missing clips are silent; priority/cooldown belong to the profile. Add source provenance before assigning clips. No voice pitch randomization.

Anchors use source-canvas pixels with the same pivot and facing transform as artwork. Individual PNG poses, not frame indices, are the supported pipeline. See moves/choreography.json for editable durations, contact events and per-pose anchors. Run tests/RosterSafety.gd for package validation and cancellation/reset checks.
