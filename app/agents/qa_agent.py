from langchain_groq import ChatGroq
from app.state import FinanceState
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.2
)
def qa_agent(state: FinanceState) -> FinanceState:
    transactions = state.get("transactions", [])
    memory = state.get("memory", [])

    sample_data = transactions[:10]

    formatted_memory = ""
    for item in memory[-5:]:
        if isinstance(item, dict):
            formatted_memory += f"User: {item.get('query')}\nAssistant: {item.get('response')}\n"

    prompt = f"""
You are a financial assistant.
STRICT RULES:
- ONLY use provided data
- DO NOT assume missing values
- If data is insufficient → say "Insufficient data"
- DO NOT hallucinate

Sample Transactions:
{sample_data}

Conversation History:
{formatted_memory}

User Question:
{state['user_query']}
"""

    state["response"] = llm.invoke(prompt).content
    return state