"""Duration/identity gates for all future 5–6 regular-move authoring."""
import copy
import json
import unittest

from tools.director_move_qa import (
    ROOT, MIN_NORMAL_TICKS, MAX_NORMAL_TICKS, read_tres, longest_common_run,
    assess_new_normal, legacy_audit, hit_pose_paths
)


class NewNormalQualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.moves = json.loads((ROOT / "moves/choreography.json").read_text())["moves"]
        cls.new = read_tres(ROOT / "moves/director_drafts/chunli_neutral_b_preview.tres")
        cls.baseline = read_tres(ROOT / "moves/director_drafts/chunli_neutral_b_baseline.tres")

    def test_approved_design_contract_targets_2_to_5_seconds(self):
        self.assertEqual((MIN_NORMAL_TICKS, MAX_NORMAL_TICKS), (120, 300))
        self.assertEqual(self.new["duration_ticks"], 156)
        self.assertEqual(len(self.new["hit_events"]), 9)
        self.assertEqual(len(self.new["poses"]), 20)
        report=assess_new_normal(self.new,self.moves)
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["duration_seconds"], 2.6)
        self.assertEqual(report["visual_contact_verdict"][:10], "UNVERIFIED")

    def test_original_88_tick_version_remains_untouched(self):
        self.assertEqual(self.baseline["duration_ticks"], 88)
        self.assertEqual(len(self.baseline["hit_events"]), 5)
        for old,new in zip(self.baseline["hit_events"],self.new["hit_events"][:5]):
            self.assertEqual(old["tick"], new["tick"])
            self.assertEqual(old["region"], new["region"])
        self.assertEqual(self.new["poses"][:9], self.baseline["poses"][:9])

    def test_new_kicks_are_sourced_to_appropriate_visible_poses(self):
        expected=["1685_13.png", "1685_14.png", "1565_13.png", "1565_14.png"]
        source=hit_pose_paths(self.new)[-4:]
        self.assertEqual([p.split("/")[-1] for p in source], expected)
        self.assertEqual([e["tick"] for e in self.new["hit_events"][-4:]], [94,101,117,124])
        self.assertEqual([e["damage"] for e in self.new["hit_events"][-4:]], [5,5,5,5])

    def test_short_new_regular_attack_is_blocked_but_legacy_is_debt(self):
        short = copy.deepcopy(self.new)
        short["duration_ticks"] = 88
        result=assess_new_normal(short,[])
        self.assertTrue(any("2–5 seconds" in e for e in result["errors"]))
        self.assertGreater(len(legacy_audit(self.moves)["legacy_normals_outside_duration_target"]),0)

    def test_exact_attack_copy_and_same_hit_phrase_are_rejected(self):
        peer=copy.deepcopy(self.new)
        peer["sequence_id"]="chunli_clone"
        bad=assess_new_normal(self.new,[peer])
        self.assertTrue(any("Near-duplicate visual phrase" in msg for msg in bad["errors"]))
        self.assertTrue(any("Identical striking-pose motif" in msg for msg in bad["errors"]))

    def test_shared_individual_stance_does_not_prohibit_new_sequences(self):
        a=["stance","kick_a","kick_b","recover"]
        b=["stance","kick_c","kick_d","recover"]
        self.assertEqual(longest_common_run(a,b),1)

    def test_kick_combos_cannot_knock_down_before_later_hits(self):
        self.assertEqual(self.new["hit_events"][6]["reaction"], "sustain")
        self.assertEqual(self.new["hit_events"][6]["launch"], 65)
        bad=copy.deepcopy(self.new)
        bad["hit_events"][6]["reaction"]="finish"
        self.assertTrue(any("Premature finisher" in x
                            for x in assess_new_normal(bad,[])["errors"]))

    def test_hit_ids_are_unique(self):
        changed=copy.deepcopy(self.new)
        changed["hit_events"][1]["id"]=changed["hit_events"][0]["id"]
        self.assertTrue(any("Duplicate hit event" in s for s in assess_new_normal(changed,[])["errors"]))


if __name__=="__main__":
    unittest.main()
