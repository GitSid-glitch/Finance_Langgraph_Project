import streamlit as st
import json
import pandas as pd
from dotenv import load_dotenv
load_dotenv()
from app.graph import build_graph
from app.tools.data_processor import parse_file, dataframe_to_transactions
@st.cache_resource
def get_graph():
    return build_graph()
app = get_graph()
st.set_page_config(page_title="Finance AI Assistant", layout="wide")

st.title("💰 Finance AI Assistant")
st.write("Upload your financial file (CSV, Excel, PDF, JSON) or paste JSON data.")
uploaded_file = st.file_uploader(
    "Upload financial file",
    type=["json", "csv", "xlsx", "pdf"]
)

manual_input = st.text_area(
    "Or paste transaction data (JSON format)",
    placeholder='[{"id":1,"amount":5000},{"id":2,"amount":120000}]'
)
transactions = None
if uploaded_file is not None:
    try:
        transactions = parse_file(uploaded_file)
        st.success(f"Loaded {len(transactions)} transactions from file")
    except Exception as e:
        st.error(f"Error processing file: {e}")
        st.stop()
elif manual_input.strip():
    try:
        raw_data = json.loads(manual_input)

        df = pd.DataFrame(raw_data)
        transactions = dataframe_to_transactions(df)

        st.success(f"Loaded {len(transactions)} transactions from text input")

    except Exception as e:
        st.error(f"Invalid JSON: {e}")
        st.stop()
if transactions is not None and len(transactions) > 0:
    st.subheader("📄 Processed Transactions Preview")
    st.json(transactions[:10])
    st.write(f"Total Transactions: {len(transactions)}")
else:
    st.info("Please upload a file or paste transaction data to begin.")
st.subheader("💬 Ask a Question")
user_query = st.text_input("Enter your query:")

if st.button("Run Analysis"):
    if transactions is None or len(transactions) == 0:
        st.warning("Please upload or input data first")
        st.stop()

    if not user_query:
        st.warning("Please enter a query")
        st.stop()
    state = {
        "user_query": user_query,
        "intent": "",
        "transactions": transactions,
        "risk_score": 0.0,
        "response": "",
        "memory": []
    }
    final_state = app.invoke(state)
    st.subheader("📊 Result")
    st.write(final_state["response"])