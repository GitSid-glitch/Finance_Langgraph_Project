from app.state import FinanceState
from app.tools.finance_tools import build_profile, build_summary
def context_agent(state: FinanceState) -> FinanceState:
    transactions = state.get("transactions", [])
    schema = state.get("schema", {})
    if not transactions:
        state["summary"] = {}
        state["profile"] = {}
        return state
    summary = build_summary(transactions, schema)
    profile = build_profile(summary)
    state["summary"] = summary
    state["profile"] = profile
    state["schema"] = schema
    return state