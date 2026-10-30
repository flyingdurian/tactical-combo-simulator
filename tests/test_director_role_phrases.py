"""Move contract and genuinely different storyboard tests against the real 16-roster assets."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from tools.director_role_phrases import ROOT, build, classify, evidence, load_moves, roster_audit
from tools.director_phrase_preview import render_review


class RolePhraseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.moves = load_moves()
        cls.audit = roster_audit(cls.moves)
        cls.by_id = {m["sequence_id"]: m for m in cls.moves}

    def test_roster_contract_is_five_to_six_normals_two_supers_one_ultimate(self):
        spec = self.audit["contract"]
        self.assertEqual(spec["normal_total"], [5, 6])
        self.assertEqual(spec["neutral_combo"], [2, 3])
        self.assertEqual(spec["juggle"], 1)
        self.assertEqual(spec["launcher"], 1)
        self.assertEqual(spec["wall_carry"], 1)
        self.assertEqual(spec["supers"], 2)
        self.assertEqual(spec["ultimate"], 1)
        self.assertEqual(len(self.audit["roster"]), 16)

    def test_existing_six_have_supers_ultimate_but_neutral_alternative_is_missing(self):
        for name in ("kosmos", "chunli", "xiaoyu", "reiji", "xiaomu", "morrigan"):
            with self.subTest(name=name):
                row=self.audit["roster"][name]
                self.assertEqual(len(row["supers"]), 2)
                self.assertEqual(len(row["ultimates"]), 1)
                self.assertEqual(row["missing_roles"].get("neutral_combo"), 1)
                self.assertEqual(row["normal_count"], 5)

    def test_new_ten_are_flagged_partial_without_inventing_supers(self):
        names=("t_elos","ryu","ken","sheath","saya","dante","vergil",
               "captain_commando","natsu","juri_han")
        for name in names:
            with self.subTest(name=name):
                row=self.audit["roster"][name]
                self.assertEqual(row["missing_supers"], 2)
                self.assertEqual(row["missing_ultimates"], 1)
                self.assertEqual(row["status"], "incomplete")

    def test_wall_carry_requires_mechanical_evidence_not_just_name(self):
        move=self.by_id["chunli_right"]
        self.assertEqual(classify(move), "wall_carry")
        self.assertTrue(any("no explicit positive knockback" in x for x in evidence(move, "wall_carry")))

    def test_all_16_characters_generate_distinct_proposals(self):
        for name in self.audit["roster"]:
            with self.subTest(name=name):
                original = copy.deepcopy([m for m in self.moves if m.get("character")==name])
                proposal = build(name, self.moves)
                after = [m for m in self.moves if m.get("character")==name]
                self.assertEqual(original, after)
                self.assertTrue(proposal["no_runtime_changes"])
                self.assertFalse(proposal["visual_approval"])
                self.assertEqual(len(proposal["candidates"]), 3)
                paths = [tuple(c["source_poses"]) for c in proposal["candidates"].values()]
                self.assertEqual(len(set(paths)), 3)
                for candidate in proposal["candidates"].values():
                    self.assertEqual(candidate["slot_proposal"], "neutral_combo_2")
                    self.assertIn("UNAPPROVED", candidate["status"])
                    self.assertEqual(candidate["duration_ticks"],
                                     sum(f["ticks"] for f in candidate["frame_track"]))
                    self.assertGreaterEqual(len(candidate["impact_proposals"]), 2)
                    self.assertTrue(all(h["damage"] is None and not h["contact_verified"]
                                        for h in candidate["impact_proposals"]))
                    self.assertTrue(all(f["semantic_confidence"] == "unverified"
                                        for f in candidate["frame_track"]))
                    self.assertTrue(all(self.by_id[f["source_sequence_id"]]["character"]==name
                                        for f in candidate["frame_track"]))

    def test_html_preview_is_self_contained_and_review_only(self):
        proposal=build("chunli", self.moves)
        with tempfile.TemporaryDirectory() as td:
            file=Path(td)/"review.html"
            render_review(proposal, file, ROOT)
            text=file.read_text()
            self.assertIn("data:image/png;base64,", text)
            self.assertIn("UNAPPROVED STORYBOARDS", text)
            self.assertIn("precision", text)
            self.assertIn("requestAnimationFrame", text)
            self.assertGreater(file.stat().st_size, 10000)


if __name__ == "__main__":
    unittest.main()
