# Roster 5 — playable content checkpoint

Godot 4.4.1, GDScript, Compatibility. The prior ImpactCinema4 version is recoverable through the project file's version history. Tactical flow remains archived. No simultaneous mode was added.

## Implemented

KOS-MOS now deploys a slim elevated weapon attached to explicit rear-grip, fore-grip and muzzle anchors. The continuous beam spans ticks 110–365 with nine discrete contact pulses, followed by release and aftermath. Fresh-target damage is 165 after scaling. Beam drawing never applies damage. Capture begins only on a valid connection. It remains an original prototype energy weapon, not a claimed recreation of X-BUSTER.

All six packages have five distinct normal timelines, two specials, one dedicated ultimate and one assist. Reiji and Xiaomu are independent selections. F1 choices remain pending until Launch new battle; duplicate selections exchange slots. The registry, source-facing/pivots, explicit projectile muzzle anchors, optional sound profiles and preview discovery are shared data-driven systems.

| Character | Playable slots | Art/choreography status |
|---|---|---|
| KOS-MOS | 5 normals / 2 specials / ultimate / assist | Existing content preserved; sustained-beam correction implemented; weapon/pose mapping provisional |
| Chun-Li | 5 / 2 / 1 / 1 | Authored kick sequences; sparse source playback provisional |
| Ling Xiaoyu | 5 / 2 / 1 / 1 | Authored palm/turn/sweep sequences; sparse source playback provisional |
| Reiji Arisu | 5 / 2 / 1 / 1 | Sword/gun transitions; assembled source poses; provisional |
| Xiaomu | 5 / 2 / 1 / 1 | Kick/foxfire projectiles; dedicated gun muzzle alignment; provisional |
| Morrigan Aensland | 5 / 2 / 1 / 1 | Wing/kick/orb sequences; provisional |

A populated move slot is not a claim of finished animation. New character hurt/recovery/defeat use explicit procedural recoil/tint/tilt fallbacks where dedicated art is unavailable. Portraits reuse idle art. Voices are unassigned and silent. One assist variant per character is available. No extra source sheets are currently required to run this checkpoint.

## Controls and economy

J + no direction / Left / Up / Down / Right selects neutral / sustain / launcher / finisher / carry. Directions stay screen-space on either side. U/I assists; K/L specials; O ultimate; Space meter cancel in player phase or block in CPU phase; Shift dodge; R reset; F1 debug/team/settings; F2 preview; F3 mirror; F4 explicit miss test; F5 late test; F6 CPU toggle.

Four main actions per phase. Normals spend one, assists are independent once per phase. Specials cost 90/120; ultimate 300; meter maximum 300; cancel 60 with at most one bonus action per phase. Specials/ultimate do not refund their own damage. Input/availability and authored chain windows are displayed. Reduced flash, shake, effect density, reduced camera and shortened ultimate are in F1. Shortening advances the timeline faster, preserving all events.

## Actual validation

- Godot 4.4.1 headless import succeeded after the final script changes.
- RosterAcceptance: 780 checks, zero failures: all 48 main move slots, both sides, exact grounded event counts, real intersecting contact, airborne opportunities, costs, capture/projectile cleanup and active reset.
- RosterSafety: 689 checks, zero failures: all six package validators, cancellation before/after permitted strikes, no future ghost events, ultimate reset at five timeline points per character, pending-selection isolation.
- ContinuousBeam: 8 checks, zero failures: continuous visual lifetime, mirrored muzzle attachment, nine pulses/165 damage and owner cleanup.
- AssistRoster: 84 checks, zero failures: repeated grounded contacts both sides, rising juggle, steep late-fall misses, clean exit/reset.
- Existing MilestoneAcceptance: 453 checks, zero failures; ImpactAcceptance: 80 checks, zero failures (earlier in this checkpoint before the final decorative backdrop change).
- Actual Compatibility rendering produced 153 contact screenshots in docs/contact_audit. These are scripted runtime captures, not proof that every animation is polished. Effects-disabled captures expose source-pose/contact quality. Reiji and Xiaomu contact montage review informed corrections to anticipation strikes and muzzle placement.

No browser/web export test was performed. No current-build video is claimed. Older footage and docs retained in this project are historical; this file supersedes their roster status. Headless intersection tests cannot establish perceived animation quality. Human full-speed review remains necessary.

## Pipeline and constraints

Original PNGs are retained under assets/characters/*_source. roster_manifest.json stores source rectangles (left, top, right, bottom), canvas offsets, pivots and facing. choreography.json holds per-use pose order/duration/offset/anchors and event timing. The author_roster.py recipes are explicit inspected cell selections; they do not infer animation order. Background removal preserves costume colors; source files are unchanged. No newly downloaded art or voice clips are bundled.

Use character_template/README.md, moves/kosmos.tres and moves/reiji.tres as package references. Add a package path to moves/roster.json, author resources with existing event types, validate, preview with F2 and test both sides. compile_moves.py rebuilds resources from choreography.json. author_roster.py is a content-generation recipe that overwrites authored package/move data: checkpoint before running it. upgrade_*.py are historical one-time migrations, not normal import steps.

Character controllers contain no name-based move switches. The offline extraction authoring recipe necessarily knows each sheet's layout. Sound profiles use semantic clip pools, priority/cooldown and explicit silence. Dedicated recovery/hurt art, richer pose transitions, manual ultimate pacing review and roster balance are the next content work.

## References and attribution

Supplied sheets are user-provided copyrighted character material for this personal prototype; public redistribution rights are not established. Original choreography/timings are not verified canonical move data.

- https://www.bandainamcoent.co.jp/cs/list/xenosaga2/battle/index.html — KOS-MOS energy-weapon identity; not this weapon geometry/timeline.
- https://pxz2.bn-ent.net/sp/character/36.php — Reiji identity and weapon background.
- https://pxz2.bn-ent.net/sp/character/37.php — Xiaomu fox/agent identity.
- https://tekken.com/fighters/ling-xiaoyu — martial-arts identity.
- https://www.streetfighter.com/6/fr/column/detail/wtstory20 — Chun-Li kick-oriented identity.
- https://pxz2.bn-ent.net/character/43.html — Morrigan identity.
- https://pxz2.bn-ent.net/blog/?p=108 — broad Morrigan move reference, not a recreation claim.

## Owner test

Import project.godot in Godot 4.4.1, run F6, then F1: select main and two assists and Launch new battle. Enable infinite meter to inspect O immediately. Test both sides with F3. Compare each character's J/arrow-J sequences, U/I overlap and Space cancel. Review the KOS-MOS weapon with effects reduced before increasing them. Report specific move/pose/contact issues; do not judge completeness solely from damage numbers.
