import json
from app.llm import llm
from app.state import FinanceState
def finalizer_agent(state: FinanceState) -> FinanceState:
    if state.get("response") and state.get("next_action") in {"qa", "clarify"}:
        return state
    trace = state.get("trace", [])
    summary = state.get("summary", {})
    query = state.get("user_query", "")
    prompt = f"""
You are the final response writer.

Use only the evidence below.
Do not invent data.
If the evidence is insufficient, say that clearly.
User query:
{query}
Summary:
{json.dumps(summary, ensure_ascii=False, indent=2, default=str)}
Trace:
{json.dumps(trace, ensure_ascii=False, indent=2, default=str)}
Write the final answer in a clear, useful way.
"""
    state["response"] = llm.invoke(prompt).content
    return state