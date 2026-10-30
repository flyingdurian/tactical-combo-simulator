# Director Pilot Milestone — Dante and KOS-MOS playable F2 previews

This PR adds **two new experimental regular attacks** for creative visual assessment in Godot 4.4.1. It does **not** rewrite, replace, rebalance or register any existing production fighter move. Existing Chun-Li 156t lab remains intact.

## Launch and compare

Open the current project in Godot, start the simulator, press F2 (Move Preview), and select:

- **DIRECTOR LAB: Dante · Blade / Guns / Breaker — 182t [REVIEW]**
- **DIRECTOR LAB: KOS-MOS · Heavy Break Protocol — 173t [REVIEW]**

Both should be examined at full speed **and 25% speed**, in both directions (when available), paying attention to transitions between sprite families and the target's actual reactions. Source poses are real game sprites, but the newly assembled animations have **not** had a complete human pose-semantic review. They may look mechanically credible yet still have awkward sword-to-pistol pivots or weapon poses.

## Creative direction and distinction

Dante — ~3.03 seconds, 19 sourced poses, 6 contact proposals. A sword phrase based on his existing r006 animation family leads into a separate r014 gunshot family (two real projectile events), then a r018 heavy close-range ending. This contrasts with his existing short neutral-only, firearm-only and downward attack sequences; it does not assert that these are the character's canonical techniques.

KOS-MOS — ~2.88 seconds, 16 sourced poses, 6 contact proposals. A deliberate heavy-body sequence from attack_2 builds into an attack_1 heavy upper pose, then a final low heavy attack_2 sequence. Impact pacing is more spread out and the last reaction is a true finish. Some attack_2 poses are intentionally reused from existing normals, so **visual distinctness is not certified**; evaluate whether the new combination feels like a new heavy-weapon attack rather than an expanded old one.

No new voice sounds or fabricated clip identities were added. The target hurt-expression sprite system is still missing; that work is separate.

## Engine acceptance (must pass before merging)

- Source pose identity and 120–300 tick regular-attack budget.
- All 6 authored events make genuine strike/hurtbox contact in both horizontal directions, including Dante's actual projectile collisions; no oversized catch-all rectangles.
- No dropped events from premature knockdown, invulnerability or staging distance.
- Scheduler, projectile pool and cinematic state clean up after completion and after an active reset.
- Both moves absent from all normal roster and CPU move registrations.
- Existing roster, safety, versus, Chun-Li and Python Director regression suites remain green.

The assets / hit regions are inherited from original authored source moves; additional stages and timing were individually composed and must be accepted by the engine.

**No move is automatically promoted to playable Vs CPU based solely on passing headless mechanical tests.** Human full-speed choreography review remains the acceptance decision for release.
