import streamlit as st
import sys, pathlib, os
sys.path.insert(0, str(pathlib.Path(__file__).parent))

st.set_page_config(
    page_title = 'US Legislative Chatbot',
    page_icon  = '🏛️',
    layout     = 'centered',
)

@st.cache_resource(show_spinner='Building knowledge base...')
def load_kb():
    # Load .env for local development
    from dotenv import load_dotenv
    load_dotenv()

    # On Streamlit Cloud, .env doesn't exist — read from st.secrets instead
    if not os.environ.get('ANTHROPIC_API_KEY'):
        try:
            os.environ['ANTHROPIC_API_KEY'] = st.secrets['ANTHROPIC_API_KEY']
        except Exception:
            pass  # No secrets.toml locally — key already loaded from .env

    from ingest import ingest_all, get_collection
    col = get_collection()
    if col.count() == 0:
        ingest_all()
    return col

col = load_kb()
from retrieval import answer

# ── Header ──────────────────────────────────────────────
st.title('🏛️ US Legislative Chatbot')
st.caption(
    'Ask questions about US federal bills, CBO scores, Senate rules, and legislative procedures (115th–119th Congress, 2017–2025).'
)

with st.expander('💡 Example questions to try'):
    st.markdown('- What does the Inflation Reduction Act say about Medicare drug pricing?')
    st.markdown('- How is cloture invoked in the US Senate?')
    st.markdown('- What did the CHIPS Act allocate for semiconductor manufacturing?')
    st.markdown('- How does the Congressional Review Act work?')

# ── Chat state ──────────────────────────────────────────
if 'history' not in st.session_state:
    st.session_state.history = []

for msg in st.session_state.history:
    with st.chat_message(msg['role']):
        st.markdown(msg['content'])
        if msg.get('sources'):
            with st.expander('📄 Sources'):
                for s in msg['sources']:
                    st.write(f'• {s}')
        if msg.get('tokens'):
            st.caption(f"Tokens: {msg['tokens']}")

# ── Input ───────────────────────────────────────────────
if query := st.chat_input('Ask about US legislation...'):
    st.session_state.history.append({'role': 'user', 'content': query})
    with st.chat_message('user'):
        st.markdown(query)

    with st.chat_message('assistant'):
        with st.spinner('Searching legislation...'):
            result = answer(query)
        st.markdown(result['answer'])
        with st.expander('📄 Sources used'):
            for s in result['sources']:
                st.write(f'• {s}')
        st.caption(f"Tokens: {result['total_tokens']}")

    st.session_state.history.append({
        'role'   : 'assistant',
        'content': result['answer'],
        'sources': result['sources'],
        'tokens' : result['total_tokens'],
    })

    # ── Sidebar ─────────────────────────────────────────────
    with st.sidebar:
        st.header('Knowledge Base')
        st.metric('Chunks indexed', col.count())
        st.write('Coverage: 115th–119th Congress')
        st.write('Sources: congress.gov, cbo.gov, gao.gov, everycrsreport.com')
        if st.button('Clear chat'):
            st.session_state.history = []
            st.rerun()