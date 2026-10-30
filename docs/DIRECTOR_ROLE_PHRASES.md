# Choreography Director — move roles and phrase composition

## Target contract (per playable main)

- Five or six normal attacks: **two to three neutral/combo sequences**, **one juggle/sustain**, **one launcher**, **one wall-carry/knockback**. The sixth normal may instead be a separate finisher while retaining two neutral combos.
- Exactly two supers and one distinct ultimate.
- Assists are separate from the main-move count.

The existing five directional controls remain authoritative. A second neutral combo is a *content slot*, **not** a newly bound button. A later game-design approval must decide how combo alternatives are selected; do not replace a working move or bind another input by assumption.

## Why the audit matters

Earlier main characters usually have five authored normals (neutral, left/sustain, up/launcher, right/wall, down/finisher), two specials and one ultimate. Those five normals do **not** satisfy the requested two-neutral requirement. The new ten-character roster has even more missing main roles, supers, and ultimates. The role audit reports these honestly, without adding fake filler moves.

A move's name is not proof of its mechanical behavior. Several "wall carry" moves have no explicit positive knockback or wall reaction in their hit event definitions. The engine may have additional wall behavior, but this needs an in-engine contact/wall test before the role can be certified.

## First true pose-order alternatives

The phrase composer assembles a proposed **second neutral combination** from a fighter's existing:
- neutral opener/windup,
- sustain/juggle strike phrase,
- neutral or finishing strike phrase,
- recovery section.

It generates three genuinely different **source-pose sequences** (precision, rush and finisher), not simply three retimes of an identical sequence. Each result retains its original sprite filename, source move, pose index, attack reference provenance and stage hypothesis.

This is a **visual storyboard** and is **not a compiled Godot move**. Any new cross-move transitions could look disconnected or nonsensical, and the impact proposals deliberately have null damage and unverified contact. They are prohibited from entering gameplay until pose semantics, movement, hit geometry, sound and cancellation are deliberately authored and tested.

## Running the implementation

    python -m pip install pillow==11.3.0
    python -m unittest discover -s tests -p 'test_director_*.py' -v
    python tools/director_role_phrases.py --out /tmp/director-role

The output includes `role_coverage.json`, plus per-character `storyboards.json` and self-contained `review.html` previews for Chun-Li, Dante and KOS-MOS. The preview can be opened outside the project without linked assets, but contains private sprite thumbnails and should not be republished.

The CI job uploads this as private artifact **director-role-storyboards** with a 7-day retention window.

## Next gate before live combat integration

1. Evaluate the three visual storyboards for one showcase fighter, select a viable pose order and repair visibly awkward joins.
2. Confirm specific striking limbs/weapons and actual target contact in the Godot Move Preview.
3. Build one authoritative, editable move timeline for that candidate; reuse the existing scheduler, reactions, audio buses and input-selection logic.
4. Add tests for all normals (including neutral variants), both supers, ultimate, two facing directions, grounded/airborne/wall targets, interrupts and assists.
5. Preserve all previous approved moves; never auto-promote generated storyboards.
