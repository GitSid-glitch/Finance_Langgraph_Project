import json
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from app.graph import build_graph
from app.tools.data_processor import dataframe_to_transactions, parse_file
load_dotenv()
st.set_page_config(page_title="Finance LangGraph Assistant", layout="wide")
if "transactions" not in st.session_state:
    st.session_state.transactions = []
if "memory" not in st.session_state:
    st.session_state.memory = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
@st.cache_resource
def get_graph():
    return build_graph()
app = get_graph()
st.title("💰 Finance LangGraph Assistant")
st.caption("Iterative planner–executor graph for financial reasoning.")
with st.sidebar:
    st.header("Data Input")
    uploaded_file = st.file_uploader(
        "Upload CSV, Excel, PDF, or JSON",
        type=["csv", "xlsx", "pdf", "json"],
    )
    load_file = st.button("Load uploaded file")
    st.divider()
    manual_text = st.text_area(
        "Or paste JSON data",
        placeholder='[{"date":"2024-01-01","category":"Food","amount":500,"type":"debit"}]',
        height=180,
    )
    load_manual = st.button("Use pasted JSON")
    st.divider()
    if st.button("Clear conversation"):
        st.session_state.memory = []
        st.session_state.chat_history = []
def reset_for_new_data():
    st.session_state.memory = []
    st.session_state.chat_history = []
if load_file and uploaded_file is not None:
    try:
        st.session_state.transactions = parse_file(uploaded_file)
        reset_for_new_data()
        st.sidebar.success(f"Loaded {len(st.session_state.transactions)} transactions.")
    except Exception as e:
        st.sidebar.error(f"File load failed: {e}")

if load_manual and manual_text.strip():
    try:
        raw = json.loads(manual_text)

        if isinstance(raw, dict):
            for key in ["transactions", "data", "rows", "items"]:
                if key in raw and isinstance(raw[key], list):
                    raw = raw[key]
                    break
        if not isinstance(raw, list):
            raise ValueError("Paste a JSON list or a JSON object containing a transactions list.")
        st.session_state.transactions = dataframe_to_transactions(pd.DataFrame(raw))
        reset_for_new_data()
        st.sidebar.success(f"Loaded {len(st.session_state.transactions)} transactions.")
    except Exception as e:
        st.sidebar.error(f"JSON load failed: {e}")

if st.session_state.transactions:
    with st.expander("Preview loaded data", expanded=False):
        st.write(f"Transactions loaded: {len(st.session_state.transactions)}")
        st.json(st.session_state.transactions[:10])
else:
    st.info("Load a file or paste JSON to begin.")

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
prompt = st.chat_input("Ask something about your financial data")
if prompt:
    if not st.session_state.transactions:
        st.warning("Please load data first.")
        st.stop()
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    state = {
        "user_query": prompt,
        "transactions": st.session_state.transactions,
        "memory": st.session_state.memory,
        "trace": [],
        "step": 0,
        "max_steps": 3,
        "done": False,
    }
    with st.spinner("Running LangGraph..."):
        final_state = app.invoke(state)
    response = final_state.get("response", "No response generated.")
    st.session_state.memory = final_state.get("memory", [])
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    st.rerun()