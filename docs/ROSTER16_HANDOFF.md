# Roster16 intake checkpoint

Recoverable baseline: Versus6_CheckpointA, project version7. Current work extends its registry, selection, timeline and contact systems.

## Implemented

KOS-MOS chest emitter source moves to source-canvas [135,101]. Normal beam visual/contact width54, final78 (previous34/54). Six animated aperture petals, a travelling particle envelope and narrow core make the source/discharge visibly animate. Only nine explicit events can deal damage; beam range remains300 and staging distance265.

Ten independent main/assist packages: T-elos, Ryu, Ken, Sheath, Saya, Dante, Vergil, Captain Commando, Natsu, Juri Han. Each currently has three normal sequences (neutral, sustain, finisher) and one assist. Remaining slots are explicit unavailable entries. Each has its own silent CharacterSoundProfile ready for confirmed clips. These are playable partial packages, NOT completed full movesets.

Input: J / Left+J / Down+J for the new normals. U/I assists. Existing six retain Up/Right, K/L specials and O ultimate. Space cancels during player phase, blocks during CPU phase; Shift dodge; R reset/new randomCPU; F1 team/debug; F2 preview; F3 mirror. CPU filters unavailable moves and spends meter only on available specials.

## Source inspection and authorship

Import kit original sources/research/templates are retained unchanged. It identifies1612 pose candidates and explicitly warns that source order, timing and pivots are unverified. We selected assembled poses and authored timing/contact independently. Captain Commando's sheet contains other characters; only inspected Captain rows are used. Color-based paired-sheet assignments are not treated as animation proof. Ryu's initial punch mapping was rejected during rendered review; its opener now uses visibly directed kicks.

Stable pivots are per source row, not independently centered per-frame. Per-pose facing and muzzle anchors share BattleActor's authoritative transform. integrate_ten.py and assets/import_kit/battle_mapping.json record the choices; moves/choreography.json is the compiled authoring source. Missing moves do not silently substitute another move. Ground-cover projectile assists can legitimately catch a fallen target; aerial committed attacks can miss late.

The supplied MOVESET_REFERENCE.md and moveset_research.json remain attribution/research inputs. Our names and timings are original prototypes; no exact canonical animation recreation is claimed. No additional web research or video study was performed for these ten during this intake. No voice recordings are supplied or fabricated.

## Actual validation so far

Godot4.4.1 import completed without reported script errors. RosterAcceptance:1261 checks/0failures across all16 packages and available main moves, both sides, grounded event counts/intersections, airborne opportunity, deduplication, cost, ownership cleanup and active reset. This validates simulation, not polished animation quality.

Final checks: AssistRoster224/0; RosterSafety1056/0; VersusAcceptance111/0; MilestoneAcceptance463/0. New main/assist contact, cancellation/reset, role loading and CPU use pass. Late ground-cover assists may connect after landing; those tests verify real bounded contact rather than incorrectly requiring every late call to miss.

Actual Compatibility rendering produced60 current contact stills in docs/roster16_contacts. Reviewed representative new character contacts and corrected Ken's guard-pose event, Saya's slash mapping and Dante's firing/finishing poses. A shared renderer bug stretched variable-sized imported textures to256x196 while gameplay used original pixels. BattleActor now draws texture.get_size(), keeping anchors, pivots and visible contact in one coordinate system. Existing256x196 artwork remains the same size.

Actual Godot capture: docs/Roster16_ChestDischarge.mp4, ten seconds,300 rendered frames encoded at30fps, muted. It shows the enlarged animated chest discharge, final surge and cleanup. Capture log:9hits,165damage, cinematic inactive at completion. This is scripted runtime playback, not fabricated footage. No browser/web export or performance benchmark was performed. Older milestone captures/tests are historical.

## Known unfinished work

New characters lack Up/Right normals, specials, dedicated ultimates, confirmed voices and dedicated hurt/recovery/defeat mappings. Existing procedural reactions remain. Sparse pose transitions and provisional hit staging need full-speed visual tuning. Six prior character packages remain unchanged except the KOS-MOS emitter. CPU still lacks cinematic ultimates/cancels as documented in Versus6.

## Remaining move mapping plan

The kit research identifies canonical references and separate proposed standalone concepts. The next authored pass should bind Up/Right normals, two specials and a dedicated ultimate for each new package, beginning with one visually reviewed signature sequence per character. Do not enable those slots from the supplied blank templates. The current forty timelines are explicitly prototype order/timing and require further full-speed polish; they do not complete the requested ten full movesets.

New-package completion table: all ten support main/assist selection, neutral/sustain/finisher, and one assist. All ten lack Up/Right, specials, ultimate and confirmed voices. Previous six retain their existing slots and provisional art status. No source ZIP needs to be resent.

Source preservation: original sheets and their SHA256/dimensions remain inside assets/import_kit/source_manifest.json. Source-only originals/previews use .gdignore to avoid unnecessary texture imports. No paid assets, synthesized voices or inferred voice assignments were added.
