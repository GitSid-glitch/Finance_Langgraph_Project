from app.state import FinanceState
def memory_manager(state: FinanceState) -> FinanceState:
    state["memory"].append({"query": state["user_query"], "response": state["response"]})
    return state