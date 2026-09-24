import unittest
from unittest.mock import patch
from streamlit.testing.v1 import AppTest


class UITests(unittest.TestCase):
    def test_no_key_starts_without_crash(self):
        with patch.dict('os.environ',{'OPENAI_API_KEY':''}):
            app=AppTest.from_file('app.py').run()
        self.assertFalse(app.exception)
        self.assertTrue(app.chat_input[0].disabled)

    def test_conversation_and_sources_survive_rerun(self):
        result={'content':'Verified test response','sources':[
            {'url':'https://usc.edu','title':'USC','official':True}],
            'notices':[],'review':None,'usage':{},'checked_at':'2026-09-21','api_requests':2}
        with patch.dict('os.environ',{'OPENAI_API_KEY':'sk-test-not-real'}), patch('openai.OpenAI'), patch('engine.answer',return_value=result):
            app=AppTest.from_file('app.py').run()
            app.chat_input[0].set_value('When can I drop?').run()
            self.assertFalse(app.exception)
            self.assertEqual(len(app.session_state.messages),2)
            self.assertEqual(app.session_state.messages[1]['result']['sources'][0]['title'],'USC')
            app.run()
            self.assertFalse(app.exception)
            self.assertEqual(len(app.chat_message),2)
            app.button[0].click().run()
            self.assertEqual(app.session_state.messages,[])


if __name__=='__main__':
    unittest.main()
