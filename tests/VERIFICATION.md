# Actual verification — Sequence Combat 3

Executed in Godot **4.4.1-stable**, GDScript, Compatibility renderer. These are performed checks, not proposed tests.

| Execution | Result |
|---|---|
| Headless editor import | Completed without script/resource parse errors |
| `Foundation.gd` | **30 checks, 0 failures**, initially before expansion and repeated afterward |
| `MilestoneAcceptance.gd` | **448 checks, 0 failures** |
| `ToolSmoke.gd` | **11 move-lab selections safely completed** |
| `AssistProbe3.gd` | Actual sampled timing results below |
| `RenderSequences.gd` under Xvfb / Mesa llvmpipe / Compatibility | **1,260 captured frames**, nine scripted scenarios, 42 seconds at 30fps; no script errors |

Commands (replace `godot` with your Godot4.4.1 executable):

```sh
godot --headless --path . --editor --import --quit
godot --headless --audio-driver Dummy --path . --script res://tests/Foundation.gd
godot --headless --audio-driver Dummy --path . --script res://tests/MilestoneAcceptance.gd
godot --headless --audio-driver Dummy --path . --script res://tests/ToolSmoke.gd
```

The acceptance suite checks all eight main slots on both sides, intentional hit counts and contact positions inside both regions, event deduplication, action/meter separation, direction/diagonal selection, held-key echo rejection, buffer transfer, cancels adjacent to major strikes, released-projectile policy, both assists surviving cancellation, extra-action cap, affordable meter choices after normal exhaustion, real wall contact/limits, Cross release, whiff/infinite-hit prevention, ultimate lock/double-spend/lethal cleanup, reset during projectile/Cross/cinematic states, per-hit CPU defenses and phase returns, victory/defeat, role-data availability and missing-art termination. It does not substitute a damage-number assertion for region intersection.

Tests found and fixed: obsolete travel offsets adding a second approach, Chun-Li rising-entry alignment, and premature phase completion at zero normal actions. An initial budget assertion also ran after the next phase had refilled actions; it was moved to the actual action-start transaction. See DIAGNOSIS.md.

## Recorded scenarios

`docs/SequenceCombat3_Demonstrations.mp4` is actual engine output. Scripted controls drive the normal fixed-tick simulation, local cancel/ultimate speed control, presentation and contact systems. Audio was deliberately muted. It is not a manual keyboard playtest.

| Clip start | Scenario | Recorded contacts |
|---:|---|---:|
| 0:00 | Complete neutral sequence | 2 |
| 0:03.5 | Mid-sequence cancel into Up | 3 total: resolved first thrust + launcher |
| 0:07 | Neutral, both assists, Left, Down; Cross | 13 |
| 0:10.5 | Right, physical wall bounce, Left continuation | 6; wall recorded at x1160 |
| 0:14 | Special2 into ultimate, **infinite-meter training** | 11 |
| 0:20.33 | Deliberately late Xiaoyu; heel misses and combo drops | 3 total: launcher2 + knee1 |
| 0:23.83 | Same full string with sides swapped | 13 |
| 0:27.33 | Full string, CPU perfect block/dodge, return to player | 13 player contacts; CPU hits resolved independently |
| 0:37 | Ultimate with impact FX hidden | 8 |

The effects-hidden section is also provided at quarter-speed playback in `Ultimate_NoFX_QuarterSpeed.mp4` (19.87 seconds). The underlying simulation remains unchanged. Selected source previews and actual captured frames were visually inspected, including weapon/foot direction, contact, swapped-side assist visibility, boundary rebound and effects-hidden final kick. Original PNGs were preserved.

Three final small updates after recording do not alter recorded choreography: move-lab shortcuts now use InputMap, meter-cost text reads resource values, and CPU phase entry respects an already-held block key. Headless acceptance and move-lab checks were repeated afterward.

## Assist timing samples

Delays below are simulation ticks after requesting **Up** on a fresh stationary target, including ordinary hitstop. These are sampled points, not exhaustive continuous windows.

- Chun-Li: all3 hits at delays0,24,40,50,60,70,90,100; 2 of3 at80 (late vertical partial miss).
- Xiaoyu: both hits at0,24,40,50,60,100; knee only at70,80,90 (heel passes above falling target).
- Grounded, +40 and +100 calls repeated on both sides passed the multi-hit contact tests. F4 misses all moves/assists; no attack meter or fake impact. F5 deliberately uses the +80 late-Xiaoyu case.

Limitations: scripted runtime and sampled image inspection only; no manual full-match playtest, audio listening test, browser runtime, web export, low-end performance benchmark or exhaustive input-timing search is claimed. Sparse art transitions, combo feel and balance still need hands-on feedback.
