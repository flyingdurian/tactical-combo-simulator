# Director Repertoire Identity Registry — 16 Fighters

**Status: authoring-only. Gameplay and current move assets unchanged.**

## Contracts
- Each fighter has 5 required normal roles: two different neutrals, one juggle, one launcher and one wall-carry. The sixth optional normal is a distinct finisher; if a third neutral is desired, it replaces the finisher rather than silently adding a seventh move.
- Newly authored normal moves target 120–300 simulation ticks (2–5 seconds at 60 Hz). Supers (two) and ultimate (one) have their own pace.
- The 16 `moves/director_identity_blueprints.json` entries provide **different conceptual identities** for nine authoring slots each. They are **not** claims of canonical moves or verified animation semantics.
- The generated registry binds existing move IDs, frame provenance, hit-bearing sprite images and unused PNG inventory. Missing move slots remain **UNASSIGNED**, never fabricated.
- Reuse warnings detect contiguous sprite sequences and hit-pose overlap, not equivalent physical motions. This is an initial anti-repetition audit; it cannot establish visual uniqueness on its own.

## Run

    python tools/director_repertoire.py --out /tmp/director-repertoire
    python -m unittest discover -s tests -p 'test_director_repertoire.py' -v

Inspect `/tmp/director-repertoire/review.html` for 16 characters, and the full `/tmp/director-repertoire/repertoire.json` for provenance and missing roles.

GitHub Actions stores a private 7-day `director-repertoire-16` artifact. Do not publish it outside the private repository: it refers to third-party sprite work.

## Required future gates
1. Curate each fighter's pose vocabulary based on actual readable sprite frames, move references and confidence. Unreferenced PNGs are candidates for review, not automatically valid attack frames.
2. Reserve striking phrases for distinct move roles at **whole-roster level**. Human inspection is needed to identify visual near-duplicates that use different sprite filenames.
3. Build one role-aware candidate with real attack, movement, audio and cancel tracks; test in F2 against grounded, falling, airborne, wall and mirrored target settings.
4. Verify enough distinct available poses. If insufficient, flag asset shortage rather than stretching or copying a known combo.
5. Accept actual visuals before adding to playable/CPU rosters. Target hurt-expression and hit animation art is still a separately missing layer.

**Metrics are inventory, not progress toward an approved combat roster.** The initial audit counted 16 actors, 78 authored main move definitions and 66 missing required roles (existing six normal 5/6 plus supers/ult for new ten), all mechanically/visually unapproved by this identity audit.
