"""Real-asset and safety checks for Phase 2 pilot choreography proposals."""
import copy
import json
import unittest
from tools.director_beat_composer import ROOT, STYLES, generate


class BeatComposerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        doc = json.loads((ROOT / "moves/choreography.json").read_text(encoding="utf-8"))
        cls.moves = {m["sequence_id"]: m for m in doc["moves"]}

    def test_three_real_moves_generate_candidate_bank(self):
        for name in ("chunli_neutral", "dante_neutral", "kosmos_arc"):
            with self.subTest(name=name):
                move = self.moves[name]
                bank = generate(move)
                self.assertEqual(set(bank["candidates"]), set(STYLES))
                self.assertEqual(len(bank["pose_hypotheses"]), len(move["poses"]))
                for candidate in bank["candidates"].values():
                    self.assertEqual(candidate["status"], "UNAPPROVED_AUTHORING_DRAFT")
                    self.assertEqual(sum(candidate["pose_ticks"]), move["duration_ticks"])
                    self.assertEqual(candidate["source_pose_paths"],
                                     [p["path"] for p in move["poses"]])
                    self.assertEqual(len(candidate["hit_proposals"]), len(move["hit_events"]))
                    self.assertEqual([h["original_damage"] for h in candidate["hit_proposals"]],
                                     [h["damage"] for h in move["hit_events"]])
                    for hit in candidate["hit_proposals"]:
                        self.assertFalse(hit["contact_verified"])
                        beat = candidate["beats"][hit["pose_index"]]
                        self.assertGreaterEqual(hit["proposed_tick"], beat["start_tick"])
                        self.assertLess(hit["proposed_tick"], beat["end_tick_exclusive"])
                        self.assertLess(hit["proposed_end_tick"], move["duration_ticks"])

    def test_source_remains_unchanged(self):
        move = copy.deepcopy(self.moves["dante_neutral"])
        before = copy.deepcopy(move)
        generate(move)
        self.assertEqual(move, before)

    def test_candidate_rhythms_are_distinct(self):
        bank = generate(self.moves["kosmos_arc"])
        shapes = {tuple(m["pose_ticks"]) for m in bank["candidates"].values()}
        self.assertGreaterEqual(len(shapes), 2)

    def test_unsupported_moves_fail(self):
        with self.assertRaises(ValueError):
            generate({"sequence_id": "idle", "category": "ultimate",
                      "poses": [], "hit_events": []})

    def test_timing_inconsistency_fails(self):
        move = copy.deepcopy(self.moves["chunli_neutral"])
        move["duration_ticks"] += 1
        with self.assertRaises(ValueError):
            generate(move)

    def test_role_guesses_are_never_verified(self):
        bank = generate(self.moves["chunli_neutral"])
        self.assertTrue(all(role["confidence"] == "unverified"
                            for role in bank["pose_hypotheses"]))
        self.assertTrue(any(role["role_guess"] == "candidate_contact"
                            for role in bank["pose_hypotheses"]))


if __name__ == "__main__":
    unittest.main()
