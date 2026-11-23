"""Guard sprite-derived CI artifacts while repository visibility is public.

This is deliberately text-based so it runs in the existing Director unittest gate
without additional YAML dependencies.
"""
import re
import unittest
from pathlib import Path


WORKFLOW = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "godot-ci.yml"
SENSITIVE_ARTIFACTS = (
    "director-repertoire-16",
    "director-contact-review",
    "director-role-storyboards",
    "director-transition-quality",
    "director-pose-vocabulary",
    "director-pose-review-studio",
)
PRIVATE_ONLY = "if: ${{ always() && github.event.repository.private == true }}"


class PublicArtifactGuardTests(unittest.TestCase):
    def test_sprite_derived_artifacts_require_private_repo(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        steps = re.split(r"(?=^      - name: )", workflow, flags=re.MULTILINE)
        for artifact in SENSITIVE_ARTIFACTS:
            with self.subTest(artifact=artifact):
                matches = [
                    step for step in steps
                    if re.search(r"^\s+name: " + re.escape(artifact) + r"\s*$",
                                 step, flags=re.MULTILINE)
                ]
                self.assertEqual(len(matches), 1, f"Missing or duplicate {artifact} upload")
                self.assertIn(PRIVATE_ONLY, matches[0], f"{artifact} must not publish in public CI")


if __name__ == "__main__":
    unittest.main()
