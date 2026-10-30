"""Real 16-fighter repertoire coverage, originality evidence, and source-provenance gates."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from tools.director_repertoire import (ROOT, ALL_SLOTS, MAIN_SLOTS, BLUEPRINT,
   SOURCE, compile_registry, contact_pose_paths, common_run, collisions, render_html)

class RepertoireTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.src=json.loads(SOURCE.read_text())
  cls.blueprint=json.loads(BLUEPRINT.read_text())
  cls.report=compile_registry(cls.src,cls.blueprint,ROOT)

 def test_all_sixteen_and_no_fake_approved_moves(self):
  r=self.report
  self.assertEqual(r['summary']['fighters'],16)
  self.assertTrue(r['no_playable_moves_created'])
  self.assertEqual(r['canonical_accuracy'],'NOT_RESEARCH_VERIFIED')
  self.assertEqual(len(r['characters']),16)
  self.assertEqual(r['summary']['players_completely_research_verified'],0)

 def test_every_fighter_has_unique_design_signatures(self):
  for name,row in self.report['characters'].items():
   with self.subTest(name=name):
    slots=row['role_slots']
    self.assertEqual(set(slots),set(ALL_SLOTS))
    signatures=[s['design_intent'] for s in slots.values()]
    self.assertEqual(len(set(signatures)),len(ALL_SLOTS))
    self.assertTrue(all(s['design_confidence']=='DESIGN_INTENT_UNVERIFIED' for s in slots.values()))
    self.assertTrue(all(not s['contact_verified'] for s in slots.values()))
    self.assertTrue(all(not s['original_choreography_approved'] for s in slots.values()))
    for slot in MAIN_SLOTS:
     self.assertEqual(slots[slot]['duration_target_ticks'],[120,300])

 def test_unknown_slots_are_unassigned_not_fake_content(self):
  r=self.report['characters']['dante']
  self.assertEqual(r['role_slots']['neutral_a']['source_moves'],['dante_neutral'])
  for slot in ('neutral_b','launcher','wall_carry','super_a','super_b','ultimate'):
   self.assertEqual(r['role_slots'][slot]['asset_binding'],'UNASSIGNED')
  self.assertFalse(r['missing_ultimate'] is False)
  self.assertEqual(self.report['characters']['chunli']['role_slots']['neutral_b']['source_moves'],[])
  # The experimental F2 prototype is intentionally not in authored master timelines.

 def test_imported_and_original_asset_directories(self):
  d=self.report['characters']['dante']['sprite_inventory']
  c=self.report['characters']['chunli']['sprite_inventory']
  self.assertGreater(d['available_png_count'],100)
  self.assertGreater(d['unreferenced_png_count'],100)
  self.assertEqual(d['missing_source_files'],[])
  self.assertEqual(c['missing_source_files'],[])
  self.assertTrue(all('res://' in p for p in d['unreferenced_sample']))

 def test_original_content_untouched(self):
  src=copy.deepcopy(self.src)
  blue=copy.deepcopy(self.blueprint)
  compile_registry(self.src,self.blueprint,ROOT)
  self.assertEqual(src,self.src)
  self.assertEqual(blue,self.blueprint)

 def test_exact_attack_phrase_copy_is_detectable(self):
  move=next(m for m in self.src['moves'] if m['sequence_id']=='chunli_neutral')
  clone=copy.deepcopy(move);clone['sequence_id']='chunli_neutral_copy'
  flags=collisions([move,clone])
  self.assertEqual(len(flags),1)
  self.assertTrue(flags[0]['identical_ordered_contact_sources'])
  self.assertEqual(flags[0]['shared_contiguous_source_poses'],len(move['poses']))

 def test_shared_idle_alone_is_not_a_conflict(self):
  self.assertEqual(common_run(['idle','kickA','recover'],['idle','kickB','recover']),1)
  self.assertEqual(common_run(['a','b','c'],['d','e','f']),0)

 def test_source_hit_pose_mapping_is_exact(self):
  m=next(m for m in self.src['moves'] if m['sequence_id']=='chunli_neutral')
  pose_refs=contact_pose_paths(m)
  self.assertEqual([p.split('/')[-1] for p in pose_refs],['1685_1.png','1685_4.png'])

 def test_blueprint_inventory_mismatch_is_rejected(self):
  wrong=copy.deepcopy(self.blueprint);del wrong['characters']['dante']
  with self.assertRaises(ValueError):compile_registry(self.src,wrong,ROOT)

 def test_report_html_selfcontained(self):
  h=render_html(self.report)
  self.assertIn('Choreography Director',h)
  self.assertIn('UNASSIGNED',h)
  self.assertIn('DESIGN HYPOTHESES',h)
  self.assertIn('vergil',h)

if __name__=='__main__':unittest.main()
