# Versus 6 — first roster-CPU checkpoint

## Changes

- Replaced the procedural railgun with a body-mounted particle emitter on KOS-MOS's inspected braced pose. Converging motes, a tapered turbulent envelope and travelling filaments surround a narrow continuous core. The existing final surge, reaction and cleanup remain. Source anchor is [132,111] in the pose canvas. Target-relative distance changed from390 to265 so the finite300 beam reaches from this new origin; no target teleport or enlarged contact box was introduced.
- Official Xenosaga2 material explicitly describes X-BUSTER as an abdominal discharge: https://www.bandainamcoent.co.jp/cs/list/xenosaga2/battle/index.html . Official animation reference also describes the beam: https://www.bandainamcoent.co.jp/cs/list/xenosagatheanimation/highlight/09.php . Search retrieval exposed the official text; direct access to the first page returned403. No gameplay video was watched. Heavy Particle Cascade is original provisional choreography, not verified original move data or an exact X-BUSTER recreation.
- Versus mode enabled by default. Every reset/new battle draws a random main and two distinct assists from the six-character registry. Opposing teams may share characters. CPU sprites, source-facing, anchors and move timelines are the same resources used by the player.
- CPU plans three main sequences (launcher, random normal, finisher), calls each assist once at separate times, and uses an earned-meter special when affordable. Both special slots are eligible. CPU decisions do not read block/dodge inputs. Each sequence has a visible windup; HUD shows incoming contacts. No simultaneous mode.
- CPU projectiles now resolve against the player, not the enemy target; melee and projectile damage remain contact-tested and token-deduplicated. Player block/dodge resolve each hit. Both sides start with400HP in versus mode. Existing dummy training retains120 playerHP and400 targetHP.
- Removed the move-guide overlay during CPU attacks so it does not cover the defending player.
- Added choreography_review.py: generates labeled pose-order/duration/facing/hit timing cards from existing resources. Included Chun-Li examples. See CHOREOGRAPHY_PIPELINE.md for the visual review gate and sound-profile workflow.

## What is not finished

This is an initial versus checkpoint. CPU uses normals, assists and specials; CPU cinematic ultimates and CPU meter cancels are not enabled. CPU does not yet apply its own Cross Hit suspension. Player Cross Hit/cancels/ultimates are preserved. CPU planning is intentionally simple, with fixed budgets and forgiving telegraphs; difficulty-specific tactics remain future work.

The other five movesets have NOT been comprehensively re-choreographed in this checkpoint. They retain provisional source-pose mappings. Procedural particles do not supply missing acting poses. KOS-MOS still uses a sparse braced-pose animation; the revised emitter and burst are not a claim of master-level cinematic polish. Dedicated hurt/recovery/defeat art and confirmed voice mappings remain incomplete. No new character audio was downloaded or synthesized; existing semantic profiles are ready for confirmed clips.

## Validation actually run

- VersusAcceptance:71checks/0failures: randomized unique slots, six CPU mains, actual intersected deduplicated contacts, phase return, reset, mirrored CPU specials, per-hit blocking and particle ultimate exposure/cleanup.
- RosterAcceptance:780/0; RosterSafety:689/0; MilestoneAcceptance:453/0. Existing regression scenarios explicitly run in dummy-training mode; versus has its own suite.
- Godot4.4.1 Compatibility runtime rendered eight current captures in docs/versus6_captures. Viewed body-emitter discharge and CPU-team contact frames. Mesa software rendering emitted only the expected unsupported VSync warning. No current video recording, web export, browser test or performance benchmark is claimed.

A contact intersection is not proof of excellent choreography. Human full-speed review remains necessary. Automated capture is included so pose/effect problems remain visible.

## Owner test

Open project.godot in Godot4.4.1 and run. Default is roster-versus. J + arrows select moves; U/I assist; K/L special; O ultimate; Space cancels in player phase and blocks in CPU phase; Shift dodges; R starts a new randomized opponent team. Let player grace expire to observe CPU. F1 selects your team, offers infiniteHP/meter and presentation settings. Turn off Roster versus CPU and reset for the original dummy tests. F3 swaps sides. F2 opens the move lab.

Review the particle ultimate with infinite meter, then watch a CPU phase with infinite playerHP. Inspect whether each character's attack is recognizable from its pose rhythm before adding effects/audio. The next priority is one visually reviewed signature sequence and ultimate per character, then expanding the proven beat vocabulary—not more nominal move slots.

## Recoverability

Prior Roster5_CheckpointD is preserved as version6 of the downloadable project; local Roster5_PreVersus6.zip is unchanged. This update extends those systems rather than replacing the project. ROSTER5_HANDOFF.md remains historical; this document supersedes its ultimate, CPU and current-test statements.
