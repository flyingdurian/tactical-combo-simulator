"""Director transition risk checks, grounded in real source PNG alpha masks."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from tools.director_role_phrases import ROOT, build, load_moves
from tools.director_transition_quality import audit_bank, foot_proxy, report_html


class TransitionQualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.moves = load_moves()

    def test_three_source_fighters(self):
        for char in ("chunli", "dante", "kosmos"):
            with self.subTest(char=char):
                bank = build(char, self.moves)
                snapshot = copy.deepcopy(bank)
                report = audit_bank(bank, ROOT)
                self.assertEqual(bank, snapshot)
                self.assertFalse(report["gameplay_modified"])
                self.assertTrue(report["not_a_best_choreography_ranking"])
                self.assertEqual(len(report["candidates"]), 3)
                for row in report["candidates"].values():
                    self.assertIn(row["review_priority"], ("low", "medium", "high"))
                    self.assertTrue(row["visual_verdict"].startswith("NOT_ASSESSED"))
                    self.assertEqual(len(row["transitions"]), row["pose_count"] - 1)
                    self.assertEqual(len(row["foot_proxies"]), row["pose_count"])
                    self.assertTrue(all(p["confidence"] == "UNVERIFIED_ALPHA_PROXY"
                                        for p in row["foot_proxies"]))

    def test_foot_proxy_is_geometry_not_semantics(self):
        bank = build("chunli", self.moves)
        f = bank["candidates"]["precision"]["frame_track"][0]
        p = foot_proxy(f, ROOT, {})
        self.assertEqual(len(p["foot_local"]), 2)
        self.assertEqual(p["confidence"], "UNVERIFIED_ALPHA_PROXY")

    def test_rejects_project_escape(self):
        frame = {"pose_path":"res://../../etc/passwd","anchor":[0,0],
                 "native_facing":1,"offset":[0,0]}
        with self.assertRaises(ValueError):
            foot_proxy(frame, ROOT, {})

    def test_report_exists_and_cannot_claim_quality(self):
        bank = build("dante", self.moves)
        report = audit_bank(bank, ROOT)
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder)/"review.html"
            report_html(report, out)
            self.assertTrue(out.is_file())
            self.assertIn("UNAPPROVED", out.read_text())
            self.assertIn("Geometry risk only", out.read_text())


if __name__ == "__main__":
    unittest.main()
