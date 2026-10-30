# Choreography Director — pose/contact contract (Phase 2 foundation)

The original combat system remains authoritative. This tool does not alter move data, create damage, identify character poses, or assert that contact visually occurred.

A semantic review associates each hit event with its original source pose and requires explicit labels, anchors and reviewed contact evidence before approval. Unknown means **unapproved** by design. This is the gate between a technically valid animation sequence and believable choreography.

Generate a review:

```bash
python tools/director_pose_contract.py --move chunli_neutral --output /tmp/chunli_semantic_review.json
```

The output JSON is editable. Annotate each pose with stage (unknown, anticipation, approach, contact, follow_through, recovery, airborne, hold), tags (contact, weapon_contact, projectile_release, beam_exposure), foot_anchor and contact_anchor where supported by the sprite. Set confidence to verified only after inspecting the actual sprite and stage geometry. Approve each hit only after checking the active limb or weapon and target alignment; don't infer it from event timing.

evaluate(move, review) refuses readiness if an event lacks a verified contact tag, approval, or anchor, occurs during recovery, or if the source timeline changed. It is a **semantic gate**, not a physics simulator. In-engine footage, both facing directions, airborne targets, and real contact remain mandatory.

There is no automatic promotion of review JSON into shipped moves. Further phases will add image-assisted pose suggestions, contact-aware beat composition, and side-by-side scored candidate playback.
