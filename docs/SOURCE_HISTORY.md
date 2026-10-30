> Historical extraction/research notes from the earlier checkpoint. Move assignments, facing implementation, embedded-checkpoint descriptions and timings below describe that version. Current implementation and mapping are documented in README.md and ASSET_MAPPING.md. Research was not repeated for this milestone.

# Asset mapping, provenance and research

## Inspected inputs / checkpoint

Latest code inspected: `TacticalComboPrototype_KOSMOS_FullRes_Animations.zip`.
Its source was a newer KOS-MOS-integrated variant of the previously built combat-depth
project. We read its project settings, CharacterVisual, FighterController, manifest
and milestone report before making changes. The previous report explicitly had
not run Godot; this checkpoint performs its own execution tests.

Original sheets remain unchanged:

- `assets/characters/kos_mos/source/KOS-MOS_Fiora_original_2500x11188.png`
- `assets/characters/assist_source/ChunLi_Xiaoyu_original.png` — 2500×7647 PNG RGBA.

The original KOS-MOS ZIP checkpoint is embedded. These are user-supplied game sprite
sheets; redistribution licenses were not provided. They are not presented as
original artwork or openly licensed downloads. No character artwork was downloaded
from research sites. No Fiora sprite was relabeled as another character.

## Selection / extraction

KOS-MOS uses the existing transparent full-resolution PNGs and their preserved
`assets/characters/kos_mos/manifest.json`. Only inspected sword poses
0,2,3,5,6,8,9,10,11,12,14,15 plus idle were assigned to the new main timeline.
The larger inherited set remains available but is not newly mapped wholesale.

Chun-Li uses the **blue costume and bun hairstyle** assembled kick poses at y=1685,
118×118 source regions with x strides of 120, selected columns 2–9. Her source kicks
face left: `sprite_flip_h=true` in her CharacterDefinition mirrors only presentation.
Ling Xiaoyu uses the **orange costume and pigtails** assembled poses at y=1445,
selected columns 2–7. She remains a distinct CharacterDefinition and assist sequence.
The selected idle row uses smaller, explicitly specified rectangles at y=1344.

`assets/characters/assist_manifest.json` records source SHA-256, exact rectangles,
canvas offsets, authored order, tick durations and output paths. The extraction
script is `tools/extract_assists.py` (Pillow, numpy, scipy needed only for reprocessing).
Transparent removal uses edge-connected near-magenta tolerance 24 plus exact magenta
for enclosed background holes; it does not globally remove pink, purple or black.
Both originals are PNG, with no observed JPEG compression artifacts. Antialiased
magenta contour pixels may remain; aggressive color deletion was intentionally avoided.
No detached body parts were reconstructed. All frames use a 256×196 canvas and
(128,176) ground pivot. Airborne source-relative poses retain their vertical offset.

`docs/AssistPoseMapping.png` labels the selected assist poses and durations.
`moves/choreography.json` is the editable move assignment manifest. Per-pose offsets
are in display pixels; source crop offsets are in original pixels. Render scale is
1.7 with nearest filtering. Attacker travel is a separate timeline, not interpolation
between sprite drawings. Sparse poses do not create missing hand-drawn frames.

## Prototype character research (accessed 2026-10-25)

| Source URL | Evidence / use | Limits |
| --- | --- | --- |
| https://www.streetfighter.com/6/character/chunli | Capcom profile describes Chun-Li's high-kicking identity; guided rapid-kick assist | Search result retrieved; not used as PXZ2 timing evidence |
| https://www.streetfighter.com/6/character/chunli/movelist | Official command-list search result identifies kick/energy moves | Full-page fetch returned 403; no original frame data inferred |
| https://tekken.com/fighters/ling-xiaoyu | Official profile identifies Baguazhang/Piguazhang-based martial arts and links its gameplay trailer | Page inspected; embedded video was not watched or frame-analyzed |
| https://www.famitsu.com/sp/150413_pxz2/b007/ | Attributed PXZ2 feature describes KOS-MOS as a combat android and lists Fiora as her partner | Secondary publisher feature, not official original move timing |

These references guide character-appropriate **prototype** moves only. Ether Blade,
Rapid Kicks and Phoenix Lift are working labels, not claims of exact original PXZ2
move names or recreation. Actual visual pose selection comes from supplied sheets.
No verified footage timing or original event metadata was available.

## Supporting assets

Urban backdrop, target robot, sparks, arcs, trails and HUD are original procedural
GDScript drawing in this checkpoint, with no external image dependency. Audio is
an original short synthesized decaying noise/sine impact in `ImpactFX.gd`; no sampled
or purchased audio. Godot's fallback font is used, with no added font download.
Sound output was generated in-engine but not aurally playtested in this environment.
