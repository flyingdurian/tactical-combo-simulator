# Director — Transition Quality Gate (review-only)

This increment reduces wasted animation iterations by finding **which joins deserve attention first** before a storyboard is considered for the live simulator.

## Inputs / output

The existing role-aware composer generates three different neutral-combo storyboards for Chun-Li, Dante and KOS-MOS. The Transition Quality Gate examines the same real source PNGs and computes a proxy for the visible foot point and silhouette center after honoring source anchors, native facing, and authored offsets.

It marks boundary transitions between different source moves, displacement of the visible low-point and body center, repeated pose files, and overly dense hit-marker timing. A weighted **review priority** helps us choose which candidate to inspect first, rather than claiming the numerically lowest score is artistically superior.

Each character receives a portable JSON evidence report and a browser-readable transition table. Source gameplay data is not written, retimed, or overwritten.

## Usage

From the Godot root:

    python -m pip install pillow==11.3.0
    python tools/director_role_phrases.py --out /tmp/director-role
    python tools/director_transition_quality.py --source /tmp/director-role --out /tmp/director-transition
    python -m unittest discover -s tests -p 'test_director_*.py' -v

Open /tmp/director-transition/chunli/transition_report.html or inspect transition_audit.json.

CI uploads a private artifact named **director-transition-quality**. The HTML pages use no external libraries; the earlier sprite-comparison HTML is included separately in the **director-role-storyboards** artifact.

## Safety / what it does NOT solve

Lowest visible sprite point can be hair, clothing, loose weapon pieces, or airborne effects; it isn't a guaranteed foot contact. A rapid kick legitimately changes sprite silhouette and center. The report cannot judge martial-art identity, hitbox-to-limb semantics, weapon rigging, source sequence authenticity or opponent trajectory.

**No automatic approval, damage assignment, move registration or new controls are introduced.** The required 5–6 normals (2–3 neutral options, juggle, launcher, wall), 2 supers and 1 ultimate remain the authoritative long-term roster target. The next milestone must produce one properly validated Godot-playable Chun-Li neutral alternative and confirm its contact with a moving opponent in both facings.
