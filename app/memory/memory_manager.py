from app.state import FinanceState
def memory_manager(state: FinanceState) -> FinanceState:
    state["memory"].append(state["user_query"])
    state["memory"].append(state["response"])
    return state
