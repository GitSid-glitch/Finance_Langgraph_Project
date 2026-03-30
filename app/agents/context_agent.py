from app.state import FinanceState
from app.tools.finance_tools import build_profile, build_summary
def context_agent(state: FinanceState) -> FinanceState:
    transactions = state.get("transactions", [])
    summary = build_summary(transactions)
    profile = build_profile(summary)
    state["summary"] = summary
    state["profile"] = profile
    state["trace"] = state.get("trace", [])
    state["step"] = state.get("step", 0)
    state["max_steps"] = state.get("max_steps", 3)
    state["done"] = False
    return state