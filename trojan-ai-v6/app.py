import os
import streamlit as st
from openai import OpenAI, AuthenticationError, RateLimitError, APIConnectionError
from engine import answer, MODEL

st.set_page_config(page_title='TrojanAI · Reviewed', page_icon='✦', layout='centered')
st.title('✦ TrojanAI')
st.caption('Specific USC answers, with current sources and an answer review. Revision 6.1')

with st.sidebar:
    key = os.getenv('OPENAI_API_KEY', '')
    if not key:
        try:
            key = st.secrets.get('OPENAI_API_KEY', '')
        except Exception:
            key = ''
    if key:
        st.success('OpenAI API key is configured programmatically.')
    else:
        st.error('OpenAI API key is not configured.')
    st.caption('Loaded from OPENAI_API_KEY or Streamlit secrets. Never put the key in chat, source code, or screenshots.')
    profile = st.text_area('Your academic context (optional)',
        placeholder='Major, catalog year, completed courses and AP credit. No identifiers.',key='profile')
    review = st.toggle('Research + review + repair',value=True)
    st.caption('Review mode uses 2 API requests, or 4 if revision is needed. Each can use multiple searches. Costs more than a single answer; not a spending cap.')
    st.caption(f'Model: {MODEL}. Live USC research is always on.')
    if st.button('Clear conversation'):
        st.session_state.messages = []
        st.rerun()
    st.caption('Unofficial tool. Review scores are model judgments, not guaranteed accuracy. Profile remains until you clear it separately.')

if 'messages' not in st.session_state:
    st.session_state.messages = []


def show(result):
    for note in result.get('notices',[]):
        st.warning(note)
    st.markdown(result['content'])
    with st.expander('Sources and quality checks'):
        for s in result.get('sources',[]):
            st.link_button(('USC · ' if s['official'] else 'External · ') + s['title'],s['url'])
        check = result.get('review')
        if check:
            st.write('Automated review:',check.get('score'),'out of 10 (not independent human validation)')
            st.json(check)
        st.write('Research date:',result.get('checked_at'))
        st.write('API requests:',result.get('api_requests'))
        st.json(result.get('usage',{}))


for message in st.session_state.messages:
    with st.chat_message(message['role']):
        if 'result' in message:
            show(message['result'])
        else:
            st.markdown(message['content'])

question = st.chat_input('When is the last day to drop a class without hurting my GPA?',disabled=not bool(key))
if not key:
    st.info('Set OPENAI_API_KEY before starting Streamlit, then reload this page.')
if question:
    history = [{'role':m['role'],'content':m['content']} for m in st.session_state.messages]
    with st.chat_message('user'):
        st.markdown(question)
    with st.chat_message('assistant'):
        try:
            with st.status('Researching…',expanded=True) as status:
                result = answer(OpenAI(api_key=key,timeout=180,max_retries=0),question,
                                history,profile,review=review,progress=status.write)
                status.update(label='Research finished',state='complete',expanded=False)
            show(result)
            st.session_state.messages.extend([
                {'role':'user','content':question},
                {'role':'assistant','content':result['content'],'result':result}])
        except AuthenticationError:
            st.error('The configured API key was rejected. Check your environment or Streamlit secrets.')
        except RateLimitError:
            st.error('OpenAI reported a quota or rate limit. Check billing/usage, or retry later.')
        except APIConnectionError:
            st.error('Could not reach OpenAI. Check your connection and retry.')
        except Exception:
            st.error('Research or review did not finish. No answer was saved. Earlier requests may still be billed; retry when ready.')
