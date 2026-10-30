"""Director Dante / KOS-MOS pilots: no roster changes, distinct source phrases."""
import json
import unittest
from pathlib import Path

from tools.director_move_qa import ROOT, read_tres, assess_new_normal, longest_common_run, hit_pose_paths


class DirectorDualPilots(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads((ROOT / "moves/choreography.json").read_text())["moves"]
        cls.dante = read_tres(ROOT/"moves/director_drafts/dante_blade_gun_break_preview.tres")
        cls.kosmos = read_tres(ROOT/"moves/director_drafts/kosmos_heavy_break_preview.tres")

    def test_roles_lengths_and_source_originality(self):
        for move in [self.dante, self.kosmos]:
            with self.subTest(move=move["sequence_id"]):
                self.assertEqual(move["category"], "normal")
                report=assess_new_normal(move, self.original)
                self.assertEqual(report["errors"], [], report)
                self.assertGreaterEqual(move["duration_ticks"], 120)
                self.assertLessEqual(move["duration_ticks"], 300)
                self.assertGreaterEqual(len(move["poses"]), 16)
                self.assertEqual(len(move["hit_events"]), 6)
                self.assertIn("UNVERIFIED", report["visual_contact_verdict"])
                self.assertTrue(all((ROOT/p["path"][6:]).is_file() for p in move["poses"]))

    def test_dante_has_three_distinct_source_families_and_real_projectiles(self):
        paths=[p["path"] for p in self.dante["poses"]]
        self.assertEqual(len(paths), 19)
        self.assertEqual(self.dante["duration_ticks"], 182)
        self.assertTrue(any("_r006_" in p for p in paths))
        self.assertTrue(any("_r014_" in p for p in paths))
        self.assertTrue(any("_r018_" in p for p in paths))
        self.assertEqual(sum(h.get("kind") == "projectile" for h in self.dante["hit_events"]), 2)
        self.assertEqual([h["tick"] for h in self.dante["hit_events"]],
                         [36,55,85,100,147,162])
        self.assertEqual(self.dante["hit_events"][-1]["reaction"], "finish")
        self.assertTrue(all(h["reaction"] != "finish" for h in self.dante["hit_events"][:-1]))

    def test_kosmos_heavy_has_different_source_family_than_arc(self):
        paths=[p["path"] for p in self.kosmos["poses"]]
        self.assertEqual(len(paths), 16)
        self.assertEqual(self.kosmos["duration_ticks"], 173)
        self.assertTrue(any("attack_1_" in p for p in paths))
        self.assertTrue(any("attack_2_" in p for p in paths))
        self.assertEqual(self.kosmos["hit_events"][-1]["reaction"], "finish")
        self.assertTrue(all(h["reaction"] != "finish" for h in self.kosmos["hit_events"][:-1]))
        arc=next(m for m in self.original if m["sequence_id"]=="kosmos_arc")
        self.assertLess(longest_common_run(paths,[p["path"] for p in arc["poses"]]), 4)

    def test_hit_timed_poses_are_real_and_different_purposes(self):
        for move in [self.dante,self.kosmos]:
            with self.subTest(move=move["sequence_id"]):
                hits=hit_pose_paths(move)
                self.assertEqual(len(hits),6)
                self.assertGreaterEqual(len(set(hits)),4)
                self.assertEqual(len({h["id"] for h in move["hit_events"]}),6)

    def test_original_roster_json_has_not_installed_drafts(self):
        for move in [self.dante,self.kosmos]:
            self.assertFalse(any(m["sequence_id"]==move["sequence_id"] for m in self.original))
        for name in ("dante", "kosmos"):
            charter=(ROOT / "moves" / f"{name}.tres").read_text()
            self.assertNotIn("director_drafts/",charter)

    def test_source_provenance_is_not_fake_canonical_animation(self):
        for move in [self.dante,self.kosmos]:
            self.assertTrue(move["purpose"].endswith("_preview"))
            self.assertTrue(move["sequence_id"].startswith("director_"))


if __name__=="__main__":
    unittest.main()
