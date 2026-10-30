# Choreography Director — Phase 1 checkpoint

**Base:** `Roster16_CheckpointA.zip` (Library checkpoint, 2026-10-29)
**Engine:** Godot 4.4.1, GDScript, Compatibility renderer
**Scope:** additive tooling only — production timelines, combat resources, scenes and controllers unchanged.

## Implemented

- `tools/choreography_director.py` audits 96 existing timelines for syntactic/structural integrity and builds three timing candidates for an existing multi-pose normal attack:
  - `source` — exact original.
  - `snap` — reduced contact-pose durations, stronger late recovery contrast.
  - `heavy` — extended anticipation/contact poses, shorter recovery transitions.
- Retiming preserves original character, pose order, number of hit events, damage, regions, reaction profiles, and total duration. Event ticks are remapped inside their original contact poses.
- Generates editable JSON drafts, lint/metrics `review.json`, and a local interactive HTML sprite preview with hit markers, adjustable speed, and single-frame stepping.
- Generates a complete structural audit for existing moves (`docs/director_drafts/full_roster_audit.json`).
- Six Python unit tests guard proposal invariants, generator isolation, and output structure.
- GitHub Actions template in `.github/workflows/godot-ci.yml`: Python unit tests and Godot 4.4.1 headless import, RosterAcceptance, RosterSafety, and VersusAcceptance tests.

## Deliberate limits

These are **timing proposals**, not automatically authentic choreography. The generator does not identify canonical move frames, invent weapon/limb contact anchors, reconstruct missing frames, create cinematic animation, identify voice clips, or alter gameplay. Staging and cancel windows are *not retimed* and must be reviewed by gameplay tests before approved use. The generated browser preview is a visual guide, not a physics simulation.

**Do not copy JSON drafts directly into `moves/choreography.json` or replace `.tres` files before visual sign-off and engine integration tests.** Drafts contain a `_director` metadata field not accepted by the existing GDScript resource compiler; the future approval stage must remove this field and synchronize staging/cancel windows explicitly.

## Validation completed here

- Python unit tests: **6 passed**.
- Static audit: **96 original timelines, 0 structural errors**.
- Sample candidates: `chunli_neutral`, `dante_neutral`, `kosmos_arc` (3 variants each), **0 static errors**.
- Original combat source files and timeline JSON: **unchanged**.
- Godot engine execution: **not run**, Godot executable unavailable and network DNS inaccessible in this environment.
- GitHub Actions: **not run**, no game repository exists in the connected account.

## Preview and local regeneration

Open `docs/director_drafts/chunli_neutral/preview.html` in a browser **from the unzipped project folder**; similarly for Dante and KOS-MOS. You can switch Source / Snap / Heavy, Play/Pause, set quarter/half/full speed, and step ticks.

```bash
python -m unittest discover -s tests -p 'test_director_*.py' -v
python tools/choreography_director.py --audit-all
python tools/choreography_director.py --move chunli_neutral --move dante_neutral --move kosmos_arc
```

## GitHub setup (private repository)

The connected account currently exposes `pythonProject`, `solidstart`, `dump`, and `claw-and-co`; none is this game. Create a **new empty private repository** (suggested: `tactical-combo-simulator`) under `flyingdurian`, then in this project folder:

```bash
git init
git branch -M main
git add .
git commit -m "Import 16-character Battle Simulator and choreography Director Phase 1"
git remote add origin https://github.com/flyingdurian/tactical-combo-simulator.git
git push -u origin main
```

The private repository will contain game sprite assets and must stay private until all redistribution rights are cleared. Avoid committing any commercial voice ZIPs. The CI template intentionally uploads **logs and audit metadata only**, not proprietary source archives. Review repository storage and Actions artifact access before inviting collaborators.

GitHub Actions automatically runs on `main` push and pull requests and can be manually triggered. The CI workflow downloads official Godot 4.4.1 and checks its expected SHA-256. First CI execution is an integration gate, not a guaranteed pass. Separate code/asset failures from runner setup issues; do not relax failing tests just to get green results.

## Next development phase

1. Build a tagged-pose metadata index: image silhouette/anchors, contact-ready vs recovery poses, source-frame confidence, character-facing and grounded/airborne semantics.
2. Build a contact-aware beat composer from the real pose index, rejecting visually unsupported strikes and generic mirrored move templates.
3. Use headless tests for hit/cancel/reset + rendered capture reviews for choreography quality.
4. Add audio events after confirmed speaker mapping, and a manual **approval compiler** that writes approved drafts to a new branch/PR rather than mutating master.

**Acceptance boundary:** do not expand to all sixteen characters until three markedly different signature moves are approved in a real preview/playtest.
