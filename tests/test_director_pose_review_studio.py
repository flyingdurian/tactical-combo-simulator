"""Offline reviewer needs real previews and explicit manual evidence, not auto-labels."""
from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path

from tools.director_pose_vocabulary import ROOT,SOURCE,BLUEPRINT,collect_vocabulary
from tools.director_pose_review_studio import emit_studio, fighter_html


class PoseReviewStudioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=json.loads(SOURCE.read_text(encoding="utf-8"))
        cls.blueprint=json.loads(BLUEPRINT.read_text(encoding="utf-8"))
        cls.vocab=collect_vocabulary(cls.source,cls.blueprint,ROOT)

    def test_offline_sprite_gallery_with_real_file_paths(self):
        pilot={"characters":{"chunli":self.vocab["characters"]["chunli"]}}
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            info=emit_studio(pilot,root,ROOT)
            self.assertEqual(info["fighters"],1)
            self.assertGreater(info["source_thumbnails"],10)
            page=root/"fighters/chunli.html"
            self.assertTrue(page.exists())
            text=page.read_text(encoding="utf-8")
            self.assertIn('src="../thumbs/',text)
            self.assertIn("Click an actual source image",text)
            self.assertIn("VERIFIED_BY_REVIEWER",text)
            self.assertIn("Export inspected records as JSON",text)
            self.assertIn("No inspected poses selected",text)
            self.assertTrue(list((root/"thumbs").glob("*.png")))
            self.assertIn("chunli", (root/"fighters/index.html").read_text())

    def test_nonverified_art_is_not_prewritten_into_page(self):
        row=self.vocab["characters"]["chunli"]["poses"]
        page=fighter_html("chunli",{}, {}, {})
        self.assertIn("ZERO POSES AUTOMATICALLY VERIFIED",page)
        self.assertIn("reviewer",page)
        self.assertIn("card.querySelector",page)

    def test_all_fighter_names_are_safe_for_local_pages(self):
        for name in self.vocab["characters"]:
            self.assertNotIn("/",name)
            self.assertNotIn("..",name)


if __name__=="__main__":
    unittest.main()
