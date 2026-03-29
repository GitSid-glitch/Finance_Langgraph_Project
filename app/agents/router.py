from app.state import FinanceState
def router_agent(state: FinanceState) -> FinanceState:
    query = state.get("user_query", "").lower()
    if any(word in query for word in ["risk", "fraud", "suspicious"]):
        state["intent"] = "risk"
    elif any(word in query for word in [
        "total", "average", "trend", "largest",
        "remove", "compare", "revenue", "spending",
        "sum", "analysis"
    ]):
        state["intent"] = "analysis"
    else:
        state["intent"] = "qa"
    print("ROUTED TO:", state["intent"])
    return state