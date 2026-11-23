# Asset publication and CI artifact safety

**Status: OWNER DECISION REQUIRED.** This document is a publication safeguard, not a determination of sprite rights.

On 23 November 2026, GitHub reported `flyingdurian/tactical-combo-simulator` as **public**; `main` was **unprotected** and had no repository rulesets. `docs/SOURCE_HISTORY.md` states redistribution licenses were not provided for user-supplied character sprite sheets. Do not assume public availability equals permission to redistribute.

## Immediate owner actions

1. Confirm whether public repository visibility is intentional. Unless rights to redistribute all included third-party sprites are documented, **set repository visibility to private**. This does not revoke any earlier downloads, forks or cached copies.
2. Review the repository history, prior release/archive links, and existing GitHub Actions artifacts for sprite material. Audit and delete historical artifacts where appropriate; do not assume that previous artifacts labeled *private* were access-restricted while the repository was public.
3. Confirm provenance/licensing for each third-party sheet before authorizing any new public distribution, previews, or exported packages. For uncertain material, remove or replace it before republishing.
4. Configure branch protection or a ruleset for `main` requiring PR review and the CI checks. This is a repository administrative setting, not a change made by this patch.

## CI behavior after this change

The workflow still executes all existing Director and Godot tests in the runner. **Only repositories GitHub reports as private** will upload six sprite-derived Director review artifacts: `director-repertoire-16`, `director-contact-review`, `director-role-storyboards`, `director-transition-quality`, `director-pose-vocabulary`, and `director-pose-review-studio`.

Text-only Director quality and audit reports, plus headless Godot logs, retain their existing upload behavior. They are not guaranteed to be confidential in a public repository and should not contain secret data. No source sprites, master choreography, roster data or gameplay code are changed by this safety patch. The uploaded artifacts from earlier CI runs are **not** retroactively withdrawn.

A Director unittest checks that each of the six sensitive upload steps stays guarded by `github.event.repository.private == true`.

## Development gate

Do not upload extracted sprite PNGs, pose contact sheets, HTML galleries with image content, GIFs, videos or Godot exports from third-party character art to public services until rights are confirmed. Keep authored F2 moves out of normal roster/CPU registration until the product owner approves choreography at full speed and 25% speed.
