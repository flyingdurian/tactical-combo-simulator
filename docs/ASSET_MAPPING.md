# Preserved art and provisional choreography

No original sheet or extracted PNG was modified in this milestone. The enlarged `FacingAudit_Enlarged.png`, `Audit_attack_2.png`, `Audit_attack_3.png` and `AssistPoseMapping.png` remain inspectable. `moves/choreography.json` carries source rectangles, per-pose durations/order, pivot/offset, facing and move assignment. KOS-MOS source rectangles for newly reused poses were copied from the preserved extraction manifest, not guessed from a uniform grid.

- KOS-MOS sword strip `attack_1`: native strike direction right (+1), including valid back-to-camera thrust poses. Neutral uses two thrust/retract cycles; Up uses the same weapon family with an authored hop and stronger final launch. This is not claimed to recreate a canonical launcher.
- KOS-MOS bow strip `attack_3`: native left (-1), grounded aiming/release; visible arrows originate at the bow and use a bounded initial aim snapshot, never homing. Left, special 1 and ultimate's middle stage reuse these inspected weapon poses with different authored timelines.
- KOS-MOS kick strip `attack_2`: native left (-1), with retraction and extended foot poses. Right is a carry sequence; Down ends in knockdown; special 2 combines sword pickup and rising kicks; ultimate ends with two kicks. Sparse source poses limit smoothness and anticipation quality.
- Chun-Li's blue costume/buns kick strip remains Chun-Li, native left (-1). Three contact regions follow the horizontal/upward/horizontal foot poses. Entry can predict at most 32 pixels of rising target motion over six ticks, scaled by the entry height ratio. After commitment it cannot home.
- Xiaoyu's orange outfit/pigtails strip remains Xiaoyu, native left (-1). New first contact uses the bent-knee pose's local region; second uses the audited raised heel. Entry elevation remains a snapshot, preserving late vertical misses. The first hit may connect while a late heel misses: that is a partial timing failure, not fabricated full contact.
- The separately extracted `special_*` strip contains costume/weapon imagery whose sequence mapping was not established for this milestone. It is **not used** for specials or ultimate. No Fiora or unrelated fragment is relabeled as an assist character.

Source images remain PNGs; there is no new JPEG conversion or background removal. Earlier conservative magenta removal and source-relative anchors are retained. File names alone are not evidence of verified original move identity. There are no new downloaded assets, licensed audio claims or web-research claims in this milestone.

Source preview timing labels are historical; current pose durations and assignments are authoritative in choreography.json. SOURCE_HISTORY.md preserves the earlier extraction/research record explicitly as history.
