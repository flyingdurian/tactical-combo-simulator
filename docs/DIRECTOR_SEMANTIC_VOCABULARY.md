# Director Phase — Semantic Pose Vocabulary (all 16 fighters)

This is a **source-evidence and review gate**, not a claim that the computer recognizes an authentic character move. It does not alter Godot resources, source sprites, character definitions, CPU, audio or live move timing.

## Output for each fighter
- A unique per-character vocabulary of all source PNG pose paths used by the current main-move registry, with true canvas dimensions, alpha bounding boxes and occupancy.
- For every pose, original move/pose-index/timing/facing/pivot provenance.
- Source hit-event timestamp associations, including original actor-local regions, launch/knockback and reactions.
- A nine-slot move plan, each with its **distinct intended identity**, existing source association, hit-timed source paths and a reservation state.
- Cross-move hit-pose overlap warnings across normals, supers and ultimates.
- A self-contained HTML review table plus machine-readable JSON with explicit unreviewed labels.

An inferred "hit-timed pose" is **not** a confirmed kick, sword slash, weapon barrel, collision or hurt animation. The program does not apply a natural-language action label from the sprite's file name or from source category.

## Artifact commands

From the Godot project root:

    python -m pip install pillow==11.3.0
    python -m unittest discover -s tests -p 'test_director_*.py' -v
    python tools/director_pose_vocabulary.py --out /tmp/director-pose-vocabulary

Open `/tmp/director-pose-vocabulary/review.html`; use `pose_vocabulary.json` for full frame provenance. GitHub Actions uploads both as the **private**, short-retention `director-pose-vocabulary` artifact.

## Manual review / promotion gate

Future reviewed pose records should be supplied to the CLI via `--reviews /path/to/reviewed_poses.json`. Each review is keyed by character ID then the **exact res:// frame path**. The data contract is:

    {
      "schema_version": 1,
      "characters": {
        "chunli": {
          "res://assets/characters/chunli/frames/1685_1.png": {
            "status": "VERIFIED_BY_REVIEWER",
            "pose_role": "strike",
            "contact_anchor_source_px": [80, 95],
            "reviewer": "Actual reviewer name",
            "evidence_note": "Describe the visible striking limb and how this pixel was inspected."
          }
        }
      }
    }

**The example above is schema illustration only. It does NOT assert that Chun-Li's frame is verified or that the illustrated anchor is correct.** No such reviewed annotations are included by default.

The importer rejects unknown sprite paths, out-of-canvas anchors, unrecognized roles, missing reviewer identities and strikes without source-pixel anchors. Reviews must be genuine inspection notes and are not generated or approved by the model automatically.

The `compose_guard` API requires approved semantics and rejects large exact ordered source-frame copies across a fighter's repertoire. This is a **preflight**, not a license to ship. A human must review choreography, and Godot must confirm target contact and staging in both facings before gameplay integration.

## Content contract and next proof

Every complete main fighter needs **5–6 distinctive 2–5-second regular moves**, 2 supers and 1 unique cinematic ultimate. The target's missing hurt-expression animations remain a separate visual-system task. We must not fill the 66 missing required roles by naming generic recycled sprites.

Next: visually label a small, inspected pilot vocabulary, prove a second **F2-only** character-specific attack in Godot, then expand verified tags across the roster. Entire-repertoire artistic approval is **not** achieved by this milestone.
