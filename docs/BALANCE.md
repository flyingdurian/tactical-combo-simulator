# Prototype balance / 60 simulation ticks per second

Every row is one real gameplay event. Damage is pre-combo scaling. End ticks are inclusive; projectile active time is the release tick and then swept flight contact. Recovery = sequence duration minus the last authored strike interval, not a claim about original source-game frames.

| Move | Role/category | Duration | Chain window | Cancel window | Meter cost |
|---|---|---:|---|---|---:|
| Twin Ether / neutral opener | normal | 78 | 47–78 | 8–44 | 0 |
| Rapid Kicks / prototype | assist | 58 | 44–75 | 8–45 | 0 |
| Phoenix Relay / knee to rising heel | assist | 62 | 48–62 | 8–45 | 0 |
| Ether Relay / assist | assist | 78 | 47–78 | 8–44 | 0 |
| Ether Volley / sustain | normal | 70 | 48–70 | 8–38 | 0 |
| Telegraphed twin jab | normal | 126 | 126–126 | 8–45 | 0 |
| Delayed hammer | normal | 126 | 126–126 | 8–45 | 0 |
| Rising Circuit / launcher | normal | 78 | 43–78 | 8–38 | 0 |
| Vector Drive / wall carry | normal | 76 | 49–76 | 8–44 | 0 |
| Gravity Heel / knockdown | normal | 78 | 51–78 | 8–46 | 0 |
| Focused Ether / concentrated volley | special | 74 | 48–74 | 8–42 | 90 |
| Vector Lift / rescue chain | special | 84 | 57–84 | 8–52 | 120 |
| Ether Cascade / ultimate | ultimate | 190 | 191–191 | 191–191 | 300 |

Ultimate windows past completion deliberately disable normal chain/cancel. CPU has no player cancellation.

| Move / event | Startup tick | Active ticks | Damage | Hitstun | Hitstop | Launch / reaction | Knockback | Meter gain | Recovery |
|---|---:|---|---:|---:|---:|---|---|---:|---:|
| kosmos_arc / kosmos_arc_1 | 18 | 18–21 | 12 | 46 | 5 | 0 / ground | 8 impulse units | 12 | 39 |
| kosmos_arc / kosmos_arc_2 | 36 | 36–39 | 15 | 46 | 5 | 280 / launch | 8 impulse units | 12 | 39 |
| chunli_assist / chunli_assist_1 | 18 | 18–20 | 7 | 34 | 2 | 120 / sustain | 2 impulse units | 4 | 26 |
| chunli_assist / chunli_assist_2 | 24 | 24–26 | 7 | 34 | 2 | 120 / sustain | 2 impulse units | 4 | 26 |
| chunli_assist / chunli_assist_3 | 30 | 30–32 | 7 | 34 | 2 | 120 / sustain | 2 impulse units | 4 | 26 |
| xiaoyu_assist / xiaoyu_assist_1 | 17 | 17–19 | 7 | 44 | 3 | 90 / sustain | 3 impulse units | 6 | 34 |
| xiaoyu_assist / xiaoyu_assist_2 | 26 | 26–28 | 13 | 44 | 3 | 290 / rescue | 3 impulse units | 8 | 34 |
| kosmos_assist / kosmos_assist_1 | 18 | 18–21 | 12 | 46 | 5 | 0 / ground | 8 impulse units | 12 | 39 |
| kosmos_assist / kosmos_assist_2 | 36 | 36–39 | 15 | 46 | 5 | 280 / launch | 8 impulse units | 12 | 39 |
| kosmos_barrage / kosmos_barrage_1 | 18 | 18–18 | 10 | 36 | 2 | 85 / sustain | 2 impulse units | 12 | 36 |
| kosmos_barrage / kosmos_barrage_2 | 26 | 26–26 | 10 | 36 | 2 | 85 / sustain | 2 impulse units | 12 | 36 |
| kosmos_barrage / kosmos_barrage_3 | 34 | 34–34 | 10 | 36 | 2 | 85 / sustain | 2 impulse units | 12 | 36 |
| cpu_0 / cpu_0_1 | 52 | 52–54 | 16 | 14 | 3 | 0 / launch | 0 impulse units | 0 | 48 |
| cpu_0 / cpu_0_2 | 76 | 76–78 | 16 | 14 | 3 | 0 / launch | 0 impulse units | 0 | 48 |
| cpu_1 / cpu_1_1 | 70 | 70–72 | 22 | 14 | 3 | 0 / launch | 0 impulse units | 0 | 30 |
| cpu_1 / cpu_1_2 | 94 | 94–96 | 22 | 14 | 3 | 0 / launch | 0 impulse units | 0 | 30 |
| kosmos_up / kosmos_up_1 | 16 | 16–18 | 10 | 46 | 3 | 0 / ground | 0 impulse units | 12 | 40 |
| kosmos_up / kosmos_up_2 | 36 | 36–38 | 16 | 58 | 3 | 440 / launch | 0 impulse units | 12 | 40 |
| kosmos_right / kosmos_right_1 | 18 | 18–20 | 9 | 46 | 3 | 0 / ground | 0 impulse units | 12 | 32 |
| kosmos_right / kosmos_right_2 | 30 | 30–32 | 10 | 46 | 3 | 0 / ground | 0 impulse units | 12 | 32 |
| kosmos_right / kosmos_right_3 | 42 | 42–44 | 17 | 64 | 3 | 330 / launch | 1000 | 12 | 32 |
| kosmos_down / kosmos_down_1 | 18 | 18–20 | 9 | 46 | 3 | 80 / sustain | 0 impulse units | 12 | 32 |
| kosmos_down / kosmos_down_2 | 31 | 31–33 | 11 | 46 | 3 | 100 / sustain | 0 impulse units | 12 | 32 |
| kosmos_down / kosmos_down_3 | 44 | 44–46 | 24 | 46 | 7 | -450 / finish | 0 impulse units | 12 | 32 |
| kosmos_special_1 / kosmos_special_1_1 | 18 | 18–18 | 16 | 65 | 2 | 95 / sustain | 2 impulse units | 0 | 32 |
| kosmos_special_1 / kosmos_special_1_2 | 24 | 24–24 | 16 | 65 | 2 | 95 / sustain | 2 impulse units | 0 | 32 |
| kosmos_special_1 / kosmos_special_1_3 | 30 | 30–30 | 16 | 65 | 2 | 95 / sustain | 2 impulse units | 0 | 32 |
| kosmos_special_1 / kosmos_special_1_4 | 36 | 36–36 | 16 | 65 | 2 | 95 / sustain | 2 impulse units | 0 | 32 |
| kosmos_special_1 / kosmos_special_1_5 | 42 | 42–42 | 16 | 65 | 2 | 95 / sustain | 2 impulse units | 0 | 32 |
| kosmos_special_2 / kosmos_special_2_1 | 16 | 16–18 | 17 | 85 | 3 | 220 / rescue | 0 impulse units | 0 | 32 |
| kosmos_special_2 / kosmos_special_2_2 | 37 | 37–39 | 18 | 85 | 3 | 120 / sustain | 0 impulse units | 0 | 32 |
| kosmos_special_2 / kosmos_special_2_3 | 50 | 50–52 | 23 | 85 | 3 | 350 / rescue | 0 impulse units | 0 | 32 |
| kosmos_ultimate / kosmos_ultimate_1 | 24 | 24–26 | 22 | 90 | 3 | 0 / ground | 0 impulse units | 0 | 36 |
| kosmos_ultimate / kosmos_ultimate_2 | 40 | 40–42 | 25 | 90 | 3 | 280 / launch | 0 impulse units | 0 | 36 |
| kosmos_ultimate / kosmos_ultimate_3 | 76 | 76–76 | 22 | 90 | 2 | 125 / sustain | 2 impulse units | 0 | 36 |
| kosmos_ultimate / kosmos_ultimate_4 | 84 | 84–84 | 22 | 90 | 2 | 125 / sustain | 2 impulse units | 0 | 36 |
| kosmos_ultimate / kosmos_ultimate_5 | 92 | 92–92 | 22 | 90 | 2 | 125 / sustain | 2 impulse units | 0 | 36 |
| kosmos_ultimate / kosmos_ultimate_6 | 100 | 100–100 | 22 | 90 | 2 | 125 / sustain | 2 impulse units | 0 | 36 |
| kosmos_ultimate / kosmos_ultimate_7 | 136 | 136–138 | 26 | 90 | 3 | 130 / sustain | 0 impulse units | 0 | 36 |
| kosmos_ultimate / kosmos_ultimate_8 | 152 | 152–154 | 55 | 40 | 9 | -450 / finish | 0 impulse units | 0 | 36 |

## Staging

| Sequence | Contact distance | Approach | Commitment | Height ratio | Entry offset |
|---|---:|---|---:|---:|---:|
| kosmos_arc | 122 | 8–18 | 14 | 0 | 150 |
| chunli_assist | 110 | 4–16 | 12 | 0.8 | 155 |
| xiaoyu_assist | 61 | 4–16 | 12 | 1.0 | 180 |
| kosmos_assist | 122 | 8–18 | 14 | 0.6 | 150 |
| kosmos_barrage | 300 | 4–15 | 12 | 0 | 140 |
| cpu_0 | 100 | 4–40 | 38 | 0 | 140 |
| cpu_1 | 100 | 4–40 | 38 | 0 | 140 |
| kosmos_up | 122 | 8–16 | 12 | 0.65 | 150 |
| kosmos_right | 95 | 8–16 | 12 | 0.65 | 150 |
| kosmos_down | 95 | 8–16 | 12 | 0.85 | 150 |
| kosmos_special_1 | 270 | 4–15 | 12 | 0 | 140 |
| kosmos_special_2 | 105 | 8–16 | 12 | 0.55 | 150 |
| kosmos_ultimate | 122 | 8–22 | 18 | 0.55 | 150 |

Ultimate repositions only the attacker at ticks 56 and 118, to 270-pixel bow and 95-pixel kick spacing. Details, source poses, local regions and projectile speed/lifetime are editable in choreography.json. Normal arrows use speed 1500 px/s, lifetime 14 ticks, and a narrow swept region. No hitbox was enlarged for this milestone.

Combo damage scaling is 6% per preceding hit, floor 55%. Lift scaling starts after six juggle hits, decreases 5.5% per hit to floor 35%, and has a hard 24-hit rising limit. Gravity 850 px/s², height cap 200. Ordinary knockback units add five px/s each; authored carry uses direct velocity. One actual wall bounce per combo. Meter max300, cancel60 (one extra action per phase), special90/120, ultimate300.
