"""Pure-Python checks for the safe choreography draft generator (no Godot needed)."""
import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
script=ROOT/'tools/choreography_director.py'
spec=importlib.util.spec_from_file_location('choreography_director', script)
cd=importlib.util.module_from_spec(spec)
sys.modules['choreography_director']=cd
spec.loader.exec_module(cd)

class TestChoreographyDirector(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.moves={m['sequence_id']:m for m in cd.load_moves()}

    def test_all_original_tracks_have_valid_structure(self):
        offenders={}
        for move in self.moves.values():
            errors,_=cd.lint(move)
            if errors:offenders[move['sequence_id']]=errors
        self.assertEqual(offenders,{})

    def test_timing_budget_exact(self):
        self.assertEqual(cd.retime([5,10,15],[1,1,1],30), [5,10,15])
        self.assertEqual(sum(cd.retime([5,10,15],[1.1,.8,1.2],30)),30)
        with self.assertRaises(ValueError): cd.retime([2,2],[1,1],4)

    def test_proposals_do_not_mutate_gameplay_rules_or_master_file(self):
        for sid in ('chunli_neutral','dante_neutral','kosmos_arc'):
            original=copy.deepcopy(self.moves[sid])
            original_json=json.dumps(original,sort_keys=True)
            for variant in ('source','snap','heavy'):
                candidate=cd.make_candidate(original,variant)
                errors,_=cd.lint(candidate)
                self.assertEqual(errors,[],(sid,variant,errors))
                self.assertEqual(candidate['duration_ticks'],original['duration_ticks'])
                self.assertEqual(sum(p['ticks'] for p in candidate['poses']),original['duration_ticks'])
                self.assertEqual(len(candidate['hit_events']),len(original['hit_events']))
                self.assertEqual([p['path'] for p in candidate['poses']], [p['path'] for p in original['poses']])
                for a,b in zip(candidate['hit_events'],original['hit_events']):
                    self.assertEqual({k:v for k,v in a.items() if k not in ('tick','end_tick')},
                                     {k:v for k,v in b.items() if k not in ('tick','end_tick')})
                    self.assertEqual(a['id'],b['id'])
                self.assertEqual(candidate['staging'],original['staging'])
                self.assertEqual(candidate.get('cancel_open'),original.get('cancel_open'))
                self.assertEqual(candidate.get('cancel_close'),original.get('cancel_close'))
                self.assertEqual(candidate.get('cinematic_spec'),original.get('cinematic_spec'))
                self.assertEqual(json.dumps(original,sort_keys=True),original_json)

    def test_preserves_active_hit_pose(self):
        for sid in ('chunli_neutral','dante_neutral','kosmos_arc'):
            move=self.moves[sid]
            src_indices=[cd.pose_for_tick(move['poses'],int(e['tick']))[0] for e in move['hit_events']]
            for variant in ('snap','heavy'):
                draft=cd.make_candidate(move,variant)
                draft_indices=[cd.pose_for_tick(draft['poses'],int(e['tick']))[0] for e in draft['hit_events']]
                self.assertEqual(src_indices,draft_indices)
                for e in draft['hit_events']:
                    idx,_=cd.pose_for_tick(draft['poses'],int(e['tick']))
                    end_idx,_=cd.pose_for_tick(draft['poses'],int(e['end_tick']))
                    self.assertEqual(idx,end_idx)

    def test_export_is_self_contained_and_unapproved(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/'chunli_neutral'
            report=cd.generate(self.moves['chunli_neutral'],out)
            self.assertEqual(report['approval'],'NOT_APPROVED')
            self.assertIn('BANK=',(out/'preview.html').read_text())
            for name in ('source','snap','heavy'):
                self.assertTrue((out/f'{name}.json').is_file())
                self.assertEqual(report['candidates'][name]['errors'],[])
                draft=json.loads((out/f'{name}.json').read_text())
                self.assertTrue(all('path' in p for p in draft['poses']))

    def test_refuses_unrelated_pose_reconstruction(self):
        with self.assertRaises(ValueError): cd.make_candidate(self.moves['kosmos_ultimate'],'snap')

if __name__=='__main__': unittest.main()
