# Choreography Director — Contact Lab

**Status: authoring infrastructure only. No production moves are changed.**

## Geometry checked
This tool reads the actual alpha pixels in each hit-timed pose and projects them into the actor-local coordinates used by BattleActor.gd (non-tilted case). It respects the pose anchor, source-native facing, authored offset and right/left hit region mirroring. It reports alpha overlap count and the nearest visible sprite pixel to the existing strike region. The reviewer receives two annotated PNGs per hit event, one for each direction.

Pixel overlap is **not** evidence that the correct limb or weapon connected with the opponent. Cloth, effects, other body parts and loose hair may cause positive overlap. Target movement, actual stage placement, sprite tilt, elevation and hitstop still require Godot inspection. Semantic approval is never automatic.

## Synchronized authoring drafts
The Contact Lab applies one time mapping across pose durations, hit active intervals, cues, movement points, staging approach/commit/exit, chain and cancel windows, preserving all original damage/geometry. End-exclusive duration boundaries are maintained. Impossible timing budgets, cross-pose hit windows and collapsed staging windows are rejected. Only unapproved JSON drafts are written, never shipping Godot Resources.

## Run the pilot
From the Godot project root:

    python -m pip install pillow==11.3.0
    python -m unittest discover -s tests -p 'test_director_*.py' -v
    python tools/director_contact_lab.py --out /tmp/director-contact

Open each generated review.html for Chun-Li, Dante and KOS-MOS. The matching contact_review.json contains source SHA, per-event proxy evidence, and synchronized timing drafts.

The GitHub workflow saves these as a private seven-day artifact named director-contact-review. This artifact is a developer review tool and is not redistributed with the game.

## Release gate
Every move still requires verified pose meanings and correct strike limb/weapon anchors, both-facing Godot playtests against moving and airborne targets, cancel/assist/Cross Hit checks, an audition-confirmed sound map, and human judgment of choreography quality.

**Future direction:** build an efficient semantic pose editor, then compose meaningfully different pose/transition sequences rather than only retiming the same visual track.
