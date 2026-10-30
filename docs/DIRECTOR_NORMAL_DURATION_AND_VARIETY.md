# Director milestone — long regular attacks and repertoire originality

## New creative contract

At 60 simulation ticks per second, each regular attack must normally last **2–5 seconds (120–300 ticks)**. This applies to the 5–6 standard attack sequences per fighter (2–3 neutral combinations, juggle, launcher and wall carry/knockback). The two supers and the ultimate have independent cinematic-duration requirements.

More duration must mean more **purposeful choreography**, not a padded idle pose, frozen opponent or longer empty recovery. Mix strike height, rhythm, direction, body rotation, approach, contact and exit. Across a character's move list, intentional shared stance/transition poses are acceptable, but copying an attack's multi-pose phrase or hit-bearing motif is not.

The Authoring Quality Gate blocks new normals outside the 120–300 tick budget, exact repeated hit-pose motifs and very long identical ordered visual excerpts relative to existing normals. It warns about questionable 4+ pose reuse, repetitive three-frame cycles and machine-like regular hit spacing. The gate does NOT infer artistic correctness or independently inspect martial-arts identity. Human review and Godot-contact verification are still required.

**Legacy shorter attacks are migration debt, not automatically stretched.** Existing tested moves remain unchanged until intentionally re-authored to satisfy the new rule.

## Chun-Li neutral B iteration

The first 88-tick, five-hit version was visually reviewed positively (connected kicks, natural target motion, acceptable recovery), but it did not fit the requested 2–5-second duration. This new F2 preview extends it to **156 ticks / 2.6 seconds**, adding four sourced kick contacts and a further movement phrase. It uses 20 assembled poses and 9 events. The first five hit timings and rectangle geometries are identical to the version the user tested; no giant hitboxes, new voice identity assumptions or automatic gameplay promotion were used.

Both variants remain isolated in F2 Move Preview:
- DIRECTOR LAB: Chun-Li Rush Combo B — Extended 156t (UNAPPROVED)
- DIRECTOR BASELINE: Chun-Li Combo B — Original 88t

The old version has its own resource so the new rhythm can be compared against a known-good baseline. Neither is installed in Chun-Li's main move list or CPU repertoire. Existing project moves and 16-character roster stay untouched.

The four added hits re-use proven source pose/attack-region pairs from Chun-Li's existing down-kick and right-kick authored attacks. They still must pass real Godot playtests in both facing directions; source references alone do not prove contact.

## Target reaction / hurt-art gap

The real hit resolver currently applies hitstun, movement, and reactions; the specific opponent hurt facial expression and hit-animation artwork are still missing. That will be a separate opponent-reaction visual system, not a fake fix by adding excessive impact FX. The future reaction-asset layer should support hit direction, intensity, launch height, wall rebound and recovery.

## CI tests

- Python unit tests for duration, duplicate source motion, baseline preservation and pose-correct contact references.
- New preview acceptance checks for 9 events, 156 ticks, original first-five contact alignment, both facings, cleanup and authentic contact.
- Original 2,428+ Godot regression checks.

**Quality approval is still pending user playback of the updated F2 preview.**
