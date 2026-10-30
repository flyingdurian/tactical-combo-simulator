"""Contact Lab: actual-asset mirror and timing-ownership regression checks."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from tools.director_beat_composer import ROOT
from tools.director_contact_lab import contact_probe, create_review, emit_review, point_map, synced_draft


class ContactLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        doc = json.loads((ROOT / "moves/choreography.json").read_text(encoding="utf-8"))
        cls.moves = {m["sequence_id"]: m for m in doc["moves"]}

    def test_real_sprite_contact_geometry_for_pilots(self):
        for name in ("chunli_neutral", "dante_neutral", "kosmos_arc"):
            with self.subTest(name=name):
                move = self.moves[name]
                for event in move["hit_events"]:
                    right = contact_probe(move, event, facing=1)
                    left = contact_probe(move, event, facing=-1)
                    self.assertGreater(right["opaque_pixel_count_in_region"], 0)
                    self.assertEqual(right["opaque_pixel_count_in_region"],
                                     left["opaque_pixel_count_in_region"])
                    self.assertEqual(right["semantic_contact"], "UNVERIFIED")
                    self.assertEqual(right["geometry_proxy"],
                                     "visible_alpha_overlaps_attack_region")

    def test_full_timeline_retiming_and_no_gameplay_mutation(self):
        for name in ("chunli_neutral", "dante_neutral", "kosmos_arc"):
            with self.subTest(name=name):
                move = copy.deepcopy(self.moves[name])
                original = copy.deepcopy(move)
                review = create_review(move)
                self.assertEqual(move, original)
                self.assertEqual(len(review["candidates"]), 3)
                for style, candidate in review["candidates"].items():
                    draft = candidate["draft"]
                    self.assertEqual(draft["duration_ticks"], original["duration_ticks"])
                    self.assertEqual(sum(p["ticks"] for p in draft["poses"]), original["duration_ticks"])
                    self.assertEqual([p["path"] for p in draft["poses"]],
                                     [p["path"] for p in original["poses"]])
                    self.assertEqual([h["id"] for h in draft["hit_events"]],
                                     [h["id"] for h in original["hit_events"]])
                    for original_hit, new_hit in zip(original["hit_events"], draft["hit_events"]):
                        for key in ("damage", "region", "hitstun", "launch"):
                            self.assertEqual(original_hit.get(key), new_hit.get(key))
                    self.assertFalse(candidate["visual_contact_verified"])
                    self.assertIn("UNAPPROVED", candidate["status"])
                    self.assertEqual(len(draft["cues"]), len(original["cues"]))
                    self.assertEqual(draft["staging"]["exit_end"], original["duration_ticks"])

    def test_timed_cues_windows_and_staging_use_one_mapping(self):
        move = copy.deepcopy(self.moves["dante_neutral"])
        new = [13, 7, 12, 5, 11, 8, 16]  # sums to 72, source 7 poses
        self.assertEqual(sum(new), move["duration_ticks"])
        draft = synced_draft(move, new)
        old = [p["ticks"] for p in move["poses"]]
        for key in ("chain_open", "chain_close", "cancel_open", "cancel_close"):
            self.assertEqual(draft[key], point_map(old, new, move[key]))
        for key in ("approach_start", "approach_end", "exit_start", "exit_end", "commit_tick"):
            self.assertEqual(draft["staging"][key], point_map(old, new, move["staging"][key]))
        for before, after in zip(move["cues"], draft["cues"]):
            self.assertEqual(after["tick"], point_map(old, new, before["tick"]))

    def test_rejected_bad_duration(self):
        move = copy.deepcopy(self.moves["chunli_neutral"])
        with self.assertRaises(ValueError):
            synced_draft(move, [2] * len(move["poses"]))

    def test_rejected_hit_that_crosses_pose_boundary(self):
        move = copy.deepcopy(self.moves["chunli_neutral"])
        move["hit_events"][0]["end_tick"] = 24
        with self.assertRaises(ValueError):
            synced_draft(move, [p["ticks"] for p in move["poses"]])

    def test_source_boundaries_are_preserved(self):
        old = [4, 5, 6]
        new = [7, 3, 5]
        self.assertEqual(point_map(old, new, 0), 0)
        self.assertEqual(point_map(old, new, sum(old)), sum(new))
        with self.assertRaises(ValueError):
            point_map(old, new, sum(old) + 1)

    def test_output_contains_real_inspection_images_and_unapproved_json(self):
        move = self.moves["chunli_neutral"]
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "review"
            result = emit_review(move, target)
            self.assertTrue((target / "review.html").is_file())
            self.assertTrue((target / "contact_review.json").is_file())
            for i in range(len(move["hit_events"])):
                for face in ("right", "left"):
                    self.assertTrue((target / f"contact_{i:02d}_{face}.png").is_file())
            self.assertIn("UNAPPROVED", (target / "review.html").read_text())
            self.assertIn("source_sha256", result)

    def test_drafts_cannot_claim_approved_contact(self):
        move = self.moves["kosmos_arc"]
        review = create_review(move)
        self.assertTrue(all(item["normal_facing"]["semantic_contact"] == "UNVERIFIED"
                            for item in review["contact_probes"]))
        for candidate in review["candidates"].values():
            self.assertFalse(candidate["visual_contact_verified"])


if __name__ == "__main__":
    unittest.main()
