from dotenv import load_dotenv
load_dotenv()
import streamlit as st
import json
from app.graph import build_graph
st.set_page_config(page_title = "FinanceOps AI", layout = "centered")
st.title("💰 FinanceOps AI – LangGraph Agent Demo")
with open("data/sample_transactions.json") as trn:
    transactions = json.load(trn)
user_query = st.text_input(
    "Ask a finance question:",
    placeholder = "e.g. Check risk in my transactions"
)
if st.button("Run Agent"):
    app = build_graph()
    state = {
        "user_query": user_query,
        "intent": "",
        "transactions": transactions,
        "risk_score": 0.0,
        "response": "",
        "memory": []
    }
    with st.spinner("Running LangGraph agents..."):
        result = app.invoke(state)
    st.subheader("Agent Response")
    st.write(result["response"])
