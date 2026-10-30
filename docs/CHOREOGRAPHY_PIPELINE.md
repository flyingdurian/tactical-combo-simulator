# Choreography production gate

The previous implementation populated slots faster than it established visual quality. A hit-count pass validates bookkeeping, not impact or choreography. Do not mark a move finished on that basis.

## Repeatable work unit: one signature sequence

1. Write a brief: signature body mechanics, silhouette, rhythm, preferred distance, reaction purpose, sound identity. Record a source URL and exactly what it supports. Distinguish canonical identity from invented timing/name.
2. Inspect assembled original poses and choose anticipation, contact, follow-through and recovery. Record uncertain frames; do not fill slots with duplicates to claim completion.
3. Author a beat sheet in choreography.json: pose durations, source-facing, pivot and anchors, approach/commit, each contact interval, target response, pause and exit. Main movement must support the attack rather than idle sliding.
4. Run `python tools/choreography_review.py CHARACTER_ID` to generate labeled pose/timing cards. The cards expose pose reuse and where hits happen. They are review aids, not automatic choreography generation.
5. In F2 preview, step each hit with effects off. Verify the actual limb/weapon crosses the target on both sides, then test grounded/rising/falling targets. A legitimate miss remains possible.
6. Full-speed pass: is there a readable opening, rhythmic contrast, a strongest final contact and a believable recovery? Require a rendered capture before visual sign-off. Tune pose/event timing together; changing damage alone is insufficient.
7. Sound pass: map semantic attack, exertion, special, ultimate, assist, hurt, defeat and victory IDs to confirmed clips. Keep source filename/provenance, cooldown and priority. Missing clips remain explicitly silent. Do not use random pitch variation to manufacture character identity.
8. Regression: contact/dedup, cancel adjacent to every strike, assist independence, reset, mirrored staging, meter accounting and cinematic cleanup.

## Completion labels

- Playable prototype: resource loads, inputs work, contact and lifecycle tests pass.
- Visually reviewed: effects-off contact, both directions and full-speed rhythm reviewed.
- Polished: reference-supported identity, pacing, sound and finishing beat approved in gameplay.

Current new roster moves remain playable prototypes. The existing source art is sufficient to continue authoring; dedicated hurt/recovery/defeat poses and confirmed voices remain unmapped. This checkpoint does not claim all six movesets have been re-choreographed or their ultimates polished.

## Ultimate storyboard contract

Write a distinct opening, deployment/charge, connection, escalation, contrast, finisher and aftermath. Dedicated timeline only. Capture requires first valid contact; explicit owner handles release, lethal cleanup and reset. A clip list of normal moves is not a cinematic. Particle density cannot replace acting poses or target reaction. Favor one representative polished sequence per character before expanding the rest.
