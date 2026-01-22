from app.state import FinanceState
def router_agent(state: FinanceState) -> FinanceState:
    query = state["user_query"].lower()
    if "risk" in query or "fraud" in query:
        state["intent"] = "risk"
    elif "transaction" in query or "expense" in query:
        state["intent"] = "analysis"
    else:
        state["intent"] = "qa"
    return state
