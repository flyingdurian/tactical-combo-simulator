# Handoff

Implemented: five screen-space directional multi-hit normals; edge-triggered, one-slot input capture; authored chains and transactional meter cancels; independent multi-hit assists; finite target motion, wall carry/bounce and Cross release; bounded damage feedback and combo results; two specials; explicit eight-hit ultimate with real contacts, whiff/lethal/reset cleanup and reduced presentation; complete KOS-MOS prototype package, unfinished-character template/validation, 11-selection move lab; preserved alternating CPU defense/victory/defeat loop.

Playable recovery increments: pre-milestone project and Checkpoint A sequence/cancel foundation are separate ZIPs in `checkpoints/`. Final root project contains B–F content. The foundation passed30 checks before expansion; five-normal probes passed before adding specials/ultimate. Final counts and raw logs are in `tests/`.

Provisional: sparse sprite order, authored timing, hop/dash/return presentation, move names, meter prices and combo scaling. One inspected assist variant per assist character, not a full set of alternate main moves. Ultimate combines inspected sword/bow/kick strips rather than claiming unavailable original animation. No ambiguous special-strip frames or new downloaded art are used. CPU and portraits remain placeholders (portraits reuse idle assets); no character voices are mapped.

Next owner action: open `project.godot` in Godot4.4.1 and test the README strings at full speed, then F2/quarter speed for any questionable contact. No new asset is required to run this checkpoint. Additional independently identified anticipation/recovery and alternate-role poses would improve the next art pass.

Highest-impact next work: hands-on choreography/readability tuning; complete-match meter/window balancing; alternate-main character packages followed by a tested web export. Simultaneous mode remains intentionally absent.
