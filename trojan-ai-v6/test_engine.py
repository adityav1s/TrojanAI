import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import engine


def response(text='Test answer September 21, 2026 [cite]', annotated=True, status='completed'):
    ann = [{'type':'url_citation','url':'https://usc.edu/policy','title':'Policy',
            'start_index':len(text)-6,'end_index':len(text)}] if annotated else []
    data = {'output':[{'type':'web_search_call','action':{'type':'search'}},
                      {'type':'message','content':[{'type':'output_text','text':text,'annotations':ann}]}],
            'usage':{'input_tokens':100,'output_tokens':50}}
    return SimpleNamespace(output_text=text,status=status,model_dump=lambda:data)


def audit(passed=True):
    return json.dumps({'scores':{k:2 if passed else 0 for k in
        ('directness','factual_support','specificity','context','actionability')},
        'blockers':[] if passed else ['No actual deadline supplied.'],
        'improvements':[],'evidence_notes':[],'unresolved':[]})


class EngineTests(unittest.TestCase):
    def test_date_is_los_angeles(self):
        self.assertEqual(engine.clock(datetime(2026,9,22,1,tzinfo=timezone.utc)), '2026-09-21')

    def test_profile_and_followup_survive(self):
        p=json.loads(engine.payload('What next?', [{'role':'user','content':'I have AP Calc AB 4'}],
                                    'HTI freshman',datetime(2026,9,21)))
        self.assertIn('AP Calc AB',p['recent_conversation'][0]['content'])
        self.assertEqual(p['student_supplied_profile'],'HTI freshman')

    def test_missing_database_no_creation(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'missing.db'
            self.assertEqual(engine.local_notes('drop class',path=path),'')
            self.assertFalse(path.exists())

    def test_host_boundary(self):
        self.assertTrue(engine.official('https://classes.usc.edu/test'))
        self.assertFalse(engine.official('https://usc.edu.evil.com'))
        self.assertFalse(engine.safe_url('javascript:alert(1)'))

    def test_citation_conversion(self):
        text,sources=engine.render_response(response())
        self.assertIn('[[1]](<https://usc.edu/policy>)',text)
        self.assertNotIn('[cite]',text)
        self.assertEqual(len(sources),1)

    def test_structured_answer_has_fixed_layout(self):
        data = {
            'direct_answer': 'Prepare for the internal transfer review.',
            'assumptions': ['You mean the current fall cycle.'],
            'key_details': [{'label':'Deadline','detail':'October 1, 2026',
                             'source_title':'USC policy','source_url':'https://usc.edu/policy'}],
            'steps': ['Submit the application.', 'Meet with advising.'],
            'important_notes': ['Admission is not guaranteed.'],
            'follow_up': 'Which major are you targeting?'
        }
        fake = SimpleNamespace(output_text=json.dumps(data), model_dump=lambda: {
            'output': [], 'usage': {}
        })
        text, sources = engine.structured_answer(fake)
        self.assertIn('### Answer', text)
        self.assertIn('### Key details', text)
        self.assertIn('| Deadline | October 1, 2026 |', text)
        self.assertIn('### What to do next', text)
        self.assertEqual(sources[0]['url'], 'https://usc.edu/policy')

    def test_fixed_layout_removes_empty_items_and_duplicate_numbering(self):
        data = {
            'direct_answer': 'Use the internal transfer process.',
            'assumptions': [''],
            'key_details': [],
            'steps': ['1. Submit the form.', '', '2) Meet with advising.'],
            'important_notes': ['The review is competitive.', ''],
            'follow_up': None
        }
        text = engine.format_answer(data)
        self.assertIn('1. Submit the form.', text)
        self.assertIn('2. Meet with advising.', text)
        self.assertNotIn('1. 1.', text)
        self.assertNotIn('\n- \n', text)

    def test_invalid_structured_answer_fails_closed(self):
        fake = SimpleNamespace(output_text=json.dumps({'direct_answer':'Only this'}),
                               model_dump=lambda: {'output': []})
        with self.assertRaises(ValueError):
            engine.structured_answer(fake)

    def test_invalid_review_fails_closed(self):
        for text in ('null','[]','{}','broken'):
            self.assertFalse(engine.parse_audit(text)['passed'])

    def test_score_cannot_override_blocker(self):
        data=json.loads(audit()); data['blockers']=['Wrong year']
        self.assertFalse(engine.parse_audit(json.dumps(data))['passed'])

    def test_good_review(self):
        self.assertTrue(engine.parse_audit(audit())['passed'])

    def test_pass_needs_two_calls(self):
        with patch.object(engine,'request',side_effect=[response(),response(audit(),False)]):
            result=engine.answer(None,'drop deadline')
        self.assertEqual(result['api_requests'],2)
        self.assertFalse(result['repaired'])
        self.assertEqual(result['usage']['input_tokens'],200)

    def test_bad_answer_repaired_and_rechecked(self):
        replies=[response(),response(audit(False),False),response('Improved September 21, 2026 answer [cite]'),response(audit(),False)]
        with patch.object(engine,'request',side_effect=replies):
            result=engine.answer(None,'drop deadline')
        self.assertEqual(result['api_requests'],4)
        self.assertTrue(result['repaired'])
        self.assertTrue(result['review']['passed'])

    def test_persistent_failure_warns_and_stops(self):
        replies=[response(),response(audit(False),False),response(),response(audit(False),False)]
        with patch.object(engine,'request',side_effect=replies):
            result=engine.answer(None,'drop deadline')
        self.assertEqual(result['api_requests'],4)
        self.assertTrue(result['notices'])
        self.assertFalse(result['review']['passed'])

    def test_review_off_disclosed(self):
        with patch.object(engine,'request',return_value=response()):
            result=engine.answer(None,'drop deadline',review=False)
        self.assertEqual(result['api_requests'],1)
        self.assertTrue(result['notices'])

    def test_missing_citations_warns(self):
        with patch.object(engine,'request',return_value=response('Uncited',False)):
            result=engine.answer(None,'question',review=False)
        self.assertTrue(any('citation' in n for n in result['notices']))

    def test_request_limits_and_privacy(self):
        from unittest.mock import Mock
        client=Mock(); client.responses.create.return_value=response()
        engine.request(client,'rules','question')
        kw=client.responses.create.call_args.kwargs
        self.assertFalse(kw['store'])
        self.assertEqual(kw['max_tool_calls'],6)
        self.assertEqual(kw['tool_choice'],'required')
        self.assertEqual(kw['tools'][0]['filters']['allowed_domains'],['usc.edu'])

    def test_incomplete_not_accepted(self):
        from unittest.mock import Mock
        client=Mock(); client.responses.create.return_value=response(status='incomplete')
        with self.assertRaises(RuntimeError):
            engine.request(client,'rules','question')

    def test_high_score_cannot_hide_missing_date(self):
        review=engine.parse_audit(audit())
        checked=engine.enforce_checks(review,'last day to drop','Check WebReg', [{'official':True}])
        self.assertFalse(checked['passed'])

    def test_clarification_can_resolve_missing_deadline_context(self):
        review=engine.parse_audit(audit())
        checked=engine.enforce_checks(
            review,
            'When is the last day to drop?',
            '### Answer\nIt depends on your course session.\n\n'
            '### One follow-up question\nWhich session is your course in?',
            [{'official':True}])
        self.assertTrue(checked['passed'])

    def test_missing_major_blocker_becomes_unresolved_context(self):
        review=engine.parse_audit(audit())
        review['blockers']=['The target major and transfer term were not provided.']
        review['passed']=False
        checked=engine.soften_clarification_blockers(
            review,
            '### Answer\nThe process depends on your target major and term.\n\n'
            '### One follow-up question\nWhich major and term?')
        self.assertTrue(checked['passed'])
        self.assertFalse(checked['blockers'])
        self.assertTrue(checked['unresolved'])

    def test_high_score_cannot_hide_missing_citation(self):
        checked=engine.enforce_checks(engine.parse_audit(audit()),'Who handles this?', 'Answer', [])
        self.assertFalse(checked['passed'])


if __name__=='__main__':
    unittest.main()
