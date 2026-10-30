"""Pose-contract tests intentionally require positive evidence for approval."""
import unittest
from tools.director_pose_contract import pose_at, review_template, evaluate


def fixture():
    return {'sequence_id':'test_combo', 'duration_ticks':18,
            'poses':[{'path':f'res://frame{i}.png','ticks':6} for i in range(3)],
            'hit_events':[{'id':'h1','tick':7,'end_tick':9}]}


class PoseContractTests(unittest.TestCase):
    def test_pose_boundaries(self):
        self.assertEqual(pose_at(fixture()['poses'],6),1)
        self.assertEqual(pose_at(fixture()['poses'],17),2)
        with self.assertRaises(ValueError):pose_at(fixture()['poses'],18)

    def test_review_template_is_unapproved(self):
        review=review_template(fixture())
        self.assertEqual(review['hit_evidence'][0]['pose_index'],1)
        self.assertFalse(review['approved'])
        self.assertFalse(evaluate(fixture(),review)['ready_for_visual_approval'])

    def test_positive_evidence_can_pass_semantic_gate(self):
        move=fixture(); review=review_template(move)
        for p in review['poses']:p['confidence']='verified'
        review['poses'][1].update({'stage':'contact', 'tags':['weapon_contact'], 'contact_anchor':[85,36]})
        review['hit_evidence'][0]['approved_contact']=True
        result=evaluate(move,review)
        self.assertEqual(result['errors'],[])
        self.assertEqual(result['warnings'],[])
        self.assertTrue(result['ready_for_visual_approval'])

    def test_recovery_hit_is_rejected_even_when_approved(self):
        move=fixture(); review=review_template(move)
        for p in review['poses']:p['confidence']='verified'
        review['poses'][1].update({'stage':'recovery','tags':['contact'],'contact_anchor':[85,36]})
        review['hit_evidence'][0]['approved_contact']=True
        result=evaluate(move,review)
        self.assertFalse(result['ready_for_visual_approval'])
        self.assertTrue(any('recovery' in item for item in result['errors']))

    def test_stale_timeline_is_rejected(self):
        move=fixture(); review=review_template(move)
        move['duration_ticks']=19
        self.assertTrue(evaluate(move,review)['errors'])

    def test_wrong_sequence_is_rejected(self):
        move=fixture(); review=review_template(move)
        review['sequence_id']='other'
        self.assertTrue(evaluate(move,review)['errors'])


if __name__=='__main__':unittest.main()
