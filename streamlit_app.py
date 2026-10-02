import streamlit as st

from app.agent import run_agent
from app.memory import ConversationMemory

st.set_page_config(page_title="AI Price Comparator", page_icon="📊", layout="wide")

if "memory" not in st.session_state:
    st.session_state.memory = ConversationMemory()

if "history" not in st.session_state:
    st.session_state.history = []

st.title("AI Price & Market Assistant")
st.caption("Compare product prices, stock prices, and keep contextual memory for follow-up questions.")

with st.sidebar:
    st.header("Context Memory")
    recent_context = st.session_state.memory.get_recent_context(limit=5)
    if recent_context:
        for item in recent_context:
            st.markdown(f"- User: {item['user']}\n- Assistant: {item['assistant']}")
    else:
        st.info("No previous memory yet. Ask a question to create one.")

    st.markdown("---")
    st.write("Example prompts:")
    st.code("Compare MacBook Air and Dell XPS 13\nCompare AAPL and MSFT\nWhich product is cheapest under $400?")

with st.form("query_form"):
    user_query = st.text_input("Ask the assistant", placeholder="Compare product prices or stock prices")
    submitted = st.form_submit_button("Analyze")

if submitted and user_query:
    with st.spinner("Running agent..."):
        response = run_agent(user_query, st.session_state.memory)

    st.session_state.history.append({"question": user_query, "answer": response["answer"]})
    st.markdown("### Result")
    st.write(response["answer"])

    if response.get("mode") == "fallback":
        st.info("OpenAI API key not configured, so the app is running in local fallback mode.")

if st.session_state.history:
    st.markdown("### Recent interactions")
    for entry in reversed(st.session_state.history[-5:]):
        st.markdown(f"**You:** {entry['question']}")
        st.markdown(f"**Assistant:** {entry['answer']}")
        st.markdown("---")
