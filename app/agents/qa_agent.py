from langchain_groq import ChatGroq
from app.state import FinanceState
llm = ChatGroq(
    model = "llama-3.1-8b-instant",
    temperature = 0.2
)
def qa_agent(state: FinanceState) -> FinanceState:
    prompt = f"""
You are a financial assistant.
Conversation memory:
{state['memory']}
User question:
{state['user_query']}
"""
    state["response"] = llm.invoke(prompt).content
    return state
