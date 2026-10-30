# Director Lab — Chun-Li neutral-combo B (experimental playable preview)

This is the first **Godot-playable** candidate from the role-aware Director, using the current combat scheduler and hit resolver rather than an offline HTML imitation.

## Access

Open the project in Godot 4.4.1, start the battle simulator, enter F2 Move Preview, then use the move selector to find:

**DIRECTOR LAB: Chun-Li Rush Combo B (UNAPPROVED)**

The prototype is stored only as a separate resource at `res://moves/director_drafts/chunli_neutral_b_preview.tres`. It has not been added to Chun-Li's CharacterDefinition, roster slots, CPU move pool or normal battle input. No existing move or cinematic has been replaced.

## Composition

- 88-tick ten-pose string
- opening neutral kick phrase → sustain/juggle kick phrase → final recovery
- five explicit hit events using **existing** limb-range rectangles and reaction profiles, not enlarged catch-all hitboxes
- conservative provisional damage of 6 per event; XP 4 per event
- sound callouts intentionally absent until verified by the Combat Audio Audition
- single-entry staging, explicit exit and cancel/chain windows

The choice of pose order is an **unapproved** visual hypothesis, selected as a lower-discontinuity preview starting point. Source sprite semantics, balance and target movement are not yet artist-approved.

## Engine validation

The new `tests/DirectorPreviewAcceptance.gd` suite instantiates the actual battle scene, verifies the preview resource is absent from all 16 normal roster packages, executes the scheduler/target contact in both facings, verifies intersected contact and clean reset. Headless logs report exact hit counts.

The CI workflow now runs this suite after existing RosterAcceptance, RosterSafety and VersusAcceptance. Before the preview can become a normal selectable move it also needs actual F2 visual judgment and stable juggles with grounded/airborne/moving targets.

## Production move contract

Target for every complete main fighter: 5–6 normals (2–3 neutral combos, 1 juggle, 1 launcher, 1 wall-carry/knockback), 2 supers and 1 ultimate, with assists separate. This prototype represents only an **additional candidate neutral**; it does not imply the missing new-roster roles are complete.
