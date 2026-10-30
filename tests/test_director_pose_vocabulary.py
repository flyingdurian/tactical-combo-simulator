"""Source-backed semantic vocabulary, review provenance and all-16 ownership tests."""
from __future__ import annotations
import copy
import json
import tempfile
import unittest
from pathlib import Path

from tools.director_pose_vocabulary import (
    ROOT, SOURCE, BLUEPRINT, collect_vocabulary, validate_review,
    compose_guard, render_html, _source_pose,
)


class DirectorPoseVocabularyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads(SOURCE.read_text(encoding="utf-8"))
        cls.blueprint = json.loads(BLUEPRINT.read_text(encoding="utf-8"))
        cls.vocab = collect_vocabulary(cls.source, cls.blueprint, ROOT)

    def test_all_sixteen_have_source_pose_evidence(self):
        report = self.vocab
        self.assertEqual(report["summary"]["fighters"], 16)
        self.assertGreater(report["summary"]["unique_source_pose_paths"], 200)
        self.assertGreater(report["summary"]["hit_timed_pose_paths"], 30)
        self.assertEqual(report["summary"]["human_verified_pose_records"], 0)
        self.assertFalse(report["all_repertoire_roles_reviewed"])
        for name,row in report["characters"].items():
            with self.subTest(name=name):
                self.assertGreater(row["pose_count"], 0)
                self.assertEqual(len(row["slots"]), 9)
                self.assertEqual(row["readiness"], "PREPRODUCTION_REVIEW_REQUIRED")

    def test_every_source_pose_exists_and_has_real_pixel_geometry(self):
        for name, fighter in self.vocab["characters"].items():
            for path, pose in fighter["poses"].items():
                with self.subTest(name=name,path=path):
                    self.assertTrue((ROOT / path[6:]).is_file())
                    b = pose["pixels"]["alpha_bbox"]
                    size = pose["pixels"]["canvas"]
                    self.assertEqual(len(b), 4)
                    self.assertGreater(size[0], 0)
                    self.assertGreater(size[1], 0)
                    self.assertEqual(pose["semantic_review"]["status"], "UNREVIEWED")
                    self.assertGreaterEqual(pose["distinct_source_move_count"], 1)

    def test_hit_timed_pose_is_a_timestamp_not_semantic_certification(self):
        move = next(m for m in self.source["moves"] if m["sequence_id"]=="chunli_neutral")
        self.assertEqual(_source_pose(move, 17), 1)
        path = move["poses"][1]["path"]
        p = self.vocab["characters"]["chunli"]["poses"][path]
        self.assertTrue(p["hit_event_refs"])
        self.assertTrue(any(s["stage_guess"]=="hit_timed_not_contact_verified"
                            for s in p["source_uses"]))
        self.assertEqual(p["semantic_review"]["status"], "UNREVIEWED")

    def test_no_sources_are_mutated(self):
        src=copy.deepcopy(self.source)
        bp=copy.deepcopy(self.blueprint)
        collect_vocabulary(self.source,self.blueprint,ROOT)
        self.assertEqual(src,self.source)
        self.assertEqual(bp,self.blueprint)

    def test_review_rejects_missing_identity_and_fake_strike_anchor(self):
        pose = next(iter(self.vocab["characters"]["chunli"]["poses"].values()))
        path = pose["path"]
        geometry = pose["pixels"]
        with self.assertRaises(ValueError):
            validate_review(path, {"pose_role":"strike","status":"VERIFIED_BY_REVIEWER",
                                   "reviewer":"X", "evidence_note":"I looked at the source"},geometry)
        with self.assertRaises(ValueError):
            validate_review(path, {"pose_role":"strike","status":"VERIFIED_BY_REVIEWER",
                                   "contact_anchor_source_px":[999999,4],
                                   "reviewer":"Artist","evidence_note":"Inspected correct limb"},geometry)

    def test_review_provenance_is_explicit_not_generated(self):
        name = "chunli"
        pose = next(iter(self.vocab["characters"][name]["poses"].values()))
        path = pose["path"]
        review = {"pose_role":"strike","status":"VERIFIED_BY_REVIEWER",
                  "contact_anchor_source_px":[5,5], "reviewer":"Test fixture",
                  "evidence_note":"Unit test fabricated fixture, not an actual art inspection"}
        validated = validate_review(path,review,pose["pixels"])
        self.assertEqual(validated["status"],"VERIFIED_BY_REVIEWER")
        annotated = collect_vocabulary(self.source,self.blueprint,ROOT,
                         {"schema_version":1,"characters":{name:{path:review}}})
        self.assertEqual(annotated["summary"]["human_verified_pose_records"],1)
        self.assertFalse(annotated["characters"][name]["slots"]["neutral_a"]["signature_reserved"])

    def test_unknown_reviewed_sprite_cannot_be_imported(self):
        with self.assertRaises(ValueError):
            collect_vocabulary(self.source,self.blueprint,ROOT,
                {"schema_version":1,"characters":{"dante":{"res://fake/unavailable.png":{}}}})

    def test_composer_requires_semantic_review_before_promotion(self):
        move = next(m for m in self.source["moves"] if m["sequence_id"]=="dante_neutral")
        candidate = copy.deepcopy(move)
        candidate["sequence_id"]="director_dante_neutral_b_candidate"
        result = compose_guard(candidate,self.vocab)
        self.assertFalse(result["allowed"])
        self.assertTrue(any("semantic review" in reason for reason in result["reasons"]))

    def test_exact_pose_copy_is_rejected_even_without_verified_only(self):
        move = next(m for m in self.source["moves"] if m["sequence_id"]=="chunli_neutral")
        clone = copy.deepcopy(move)
        clone["sequence_id"]="fake_clone"
        result = compose_guard(clone,self.vocab,verified_only=False)
        self.assertFalse(result["allowed"])
        self.assertTrue(any("Near-identical" in reason for reason in result["reasons"]))

    def test_html_report_is_self_contained_and_unapproved(self):
        h=render_html(self.vocab)
        self.assertIn("16-fighter",h)
        self.assertIn("ARTIST REVIEW REQUIRED",h)
        self.assertIn("dante",h)
        self.assertIn("kosmos",h)
        self.assertIn("UNREVIEWED",h)


if __name__ == "__main__":
    unittest.main()
