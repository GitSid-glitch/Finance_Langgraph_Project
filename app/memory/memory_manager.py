from app.state import FinanceState
def memory_manager(state: FinanceState) -> FinanceState:
    memory = state.get("memory", [])
    memory.append(
        {
            "query": state.get("user_query", ""),
            "response": state.get("response", ""),
            "intent": state.get("next_action", ""),
        }
    )
    state["memory"] = memory
    return state