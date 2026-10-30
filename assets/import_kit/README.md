# PXZ2 Battle Simulator — 10-character asset import kit

Prepared from the user's eight uploaded original PNG sheets. This is a **private asset-preparation handoff**, not a redistributable game asset release.

## Deliverables
- `original_sources/`: original unchanged files + SHA256/dimensions in `source_manifest.json`.
- `characters/<slug>/frames/`: transparent PNG assembled-pose candidates. The original crop coordinates are included in `manifest.json`.
- `characters/<slug>/contact_sheet.png` and `previews/`: visual inspection and provisional GIF sequences.
- `tools/regenerate_pose_bank.py`: portable script to re-extract using the preserved original PNGs.
- `moveset_research.json`: sourced PXZ2 attack names, effects, and distinctly labeled franchise inspiration and proposed standalone Battle Simulator move concepts.
- `move_timeline_templates.json`: editable per-character move slots with **no made-up hit timings** or voice assignments.
- `godot_import/generate_spriteframes.gd`: **optional** Godot 4.x EditorScript to generate local SpriteFrames resources. No project changes have been made.

## Source sheets inspected
- `3DS - Project X Zone 2 - Enemies - Juri Han.png` — 2500 × 1910, SHA-256 `4cc5b2776e728d9c300605848026595ede1be3f01a85d30b9d33c44e37d6ce9a`
- `3DS - Project X Zone 2 - Enemies - Saya.png` — 2500 × 1716, SHA-256 `9d419b26cde330ed2ba8a04273cdbdca092833944904cb790fce589e223c385e`
- `3DS - Project X Zone 2 - Enemies - Sheath.png` — 2500 × 2253, SHA-256 `28e8d3ccef2840a483b40a135b06fc3f20334f2dfb48508dd212d0ff5cfbab5a`
- `3DS - Project X Zone 2 - Enemies - T-elos.png` — 2500 × 2301, SHA-256 `ba3aad2f1e9d303372c7a246b1dbc997aaf5c0d73f882390494b117fba02fdee`
- `3DS - Project X Zone 2 - Playable Characters - Captain Commando.png` — 2500 × 1914, SHA-256 `ffe5fede88375b97f0f8c036300ebdbe8d6a7c547faa0a466160b3d043ff08ed`
- `3DS - Project X Zone 2 - Playable Characters - Dante & Vergil.png` — 2500 × 12870, SHA-256 `ef620d491fb5d7493c6ee9f243b2735238b3eb1f4d022bd1eece7df8a7df0611`
- `3DS - Project X Zone 2 - Playable Characters - Natsu.png` — 2500 × 2916, SHA-256 `273aff39586edb6c80586e1075012529aad1a48e69ce68d319ff474dc8e3bf0f`
- `3DS - Project X Zone 2 - Playable Characters - Ryu & Ken Masters.png` — 2500 × 6902, SHA-256 `30a8ceabb122c0ba7e043999db36fe6f4d919750fed940e1cb5581de6806c2f9`

## Important caveats
1. **Pose bank, not final animation**. Sheet frame adjacency is not authoritative frame order, duration, attack timing, root motion or hitboxes. Candidate groups are marked unverified; do not assign names until visual review against gameplay footage.
2. Paired source sheets contain both characters; color-based split is strong but not perfect, particularly in transformed/effect-only frames. Re-check those with low/medium assignment confidence.
3. No body-part assembly was performed; the top loose-body-part atlases, portraits and isolated decorative/effect fragments were excluded. Pure-color key removal deliberately preserves opaque black artwork and most character purple pixels.
4. Frame canvas and crop location are kept unchanged inside each detected source cell. Ground anchors in the manifests are deliberately null until calibrated. Do not auto-center each moving pose: calibrate a stable feet pivot (and airborne offsets) before publishing.
5. PXZ2 roles differ: T-elos, Sheath, Saya and Juri are bosses; Captain Commando and Natsu are solo supports; Ryu/Ken and Dante/Vergil are pairs. This kit proposes **standalone** fighters, not a claim that PXZ2 used these exact move slots.
6. No voice files were provided. No audio is included or inferred.
7. Not engine-tested. Godot import helper is provided as source code but its execution against your evolving Battle Simulator build has not been verified.

## Import (without overwriting current game)
1. Copy `PXZ2_10_Character_Import_Kit/` anywhere under your Godot 4 project's `res://` root.
2. Let Godot import the PNG textures; use nearest filtering on the visual node or project CanvasItem texture filter.
3. Optionally run `godot_import/generate_spriteframes.gd` via the EditorScript runner. It produces one `generated_spriteframes.tres` per character with a static `idle` and all provisional candidate sequences.
4. Open each `contact_sheet.png` and animated GIF. Review labels, moves, feet anchors and order. Populate `move_timeline_templates.json` before triggering a move. Combat/hit state remains controlled by the simulator's existing timing system.
5. Keep original archive and source images private; check the source asset terms and rights before public redistribution.

## Research links
- pair: https://strategywiki.org/wiki/Project_X_Zone_2/Pair_Units
- solo: https://strategywiki.org/wiki/Project_X_Zone_2/Solo_Units
- sheath: https://projectxzone.fandom.com/wiki/Sheath
- saya: https://projectxzone.fandom.com/wiki/Saya
- telos: https://projectxzone.fandom.com/wiki/T-elos
- juri: https://projectxzone.fandom.com/wiki/Juri_Han
- roster: https://projectxzone.fandom.com/wiki/Project_X_Zone_2
