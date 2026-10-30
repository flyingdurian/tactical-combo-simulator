# Choreography Director — Phase 2 pilot

This PR builds on the merged pose-to-hit contract and the 16-fighter Godot checkpoint. It is **strictly authoring-only**. No production moves, damage, hitboxes, input logic, AI behaviors or audio files are rewritten.

## What is new
- Reads each existing pose's **actual transparent PNG**.
- Records alpha bounding box, occupancy, tentative bottom-most silhouette point, centroid shift, and normalized silhouette change.
- Flags likely duplicate holds and large pose discontinuities.
- Associates existing source hit events with source pose indices, explicitly **without claiming visible contact**.
- Proposes three beat distributions: **precision**, **rush** and **weight**. Pose order, duration budget, damage values and per-hit source pose association are preserved.
- Exports editable JSON plus a local browser gallery of actual sprite frames and proposed timings. The proposals are NOT accepted move data.

## Running the pilot

From the Godot project root:

```bash
python -m pip install pillow==11.3.0
python -m unittest discover -s tests -p 'test_director_*.py' -v
python tools/director_beat_composer.py
```

Open:
- `docs/director_beats/chunli_neutral/review.html`
- `docs/director_beats/dante_neutral/review.html`
- `docs/director_beats/kosmos_arc/review.html`

The respective `drafts.json` files include source SHA-256 fingerprints, all pose observations, event proposals, warnings and approval status. The gallery loads sprite assets from the project checkout; move its HTML together with the project if you need to share it.

**Important:** The existing motion and cue tracks, cancel windows, target reactions and combat damage are **not** retimed by the authoring drafts. Therefore these drafts must not be installed into live `SequenceData` until a single synchronized timeline compiler and actual Godot contact validation are in place.

## What the automatic analysis cannot know

A low point of the visible silhouette is not necessarily a foot. Differences between alpha shapes do not reveal the exact action, hit contact, weapon grip, canonical frame order, voice identity, or stage-relative physics. All stage names are hypotheses from existing hit timestamps, not observed martial-arts choreography. They remain `unverified`.

## Quality gates before a move may ship
1. Inspect source sprites and annotate anticipation/contact/recovery, weapon anchors, facing and confidence.
2. Build synchronized pose, movement, hit event, audio and cancel-window tracks from a single authority.
3. Preview on grounded/airborne targets; both facings; cross-hit/assist and reset.
4. Record actual Godot footage and review character identity, recoil, contact, impact and finisher.
5. Merge only approved candidates; never auto-promote generated drafts.

The next increment is a verified-pose tagging interface and contact-aware beat composition, not merely more timer variants.
