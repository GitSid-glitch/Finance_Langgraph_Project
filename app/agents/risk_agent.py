from app.state import FinanceState
def risk_agent(state: FinanceState) -> FinanceState:
    transactions = state.get("transactions", [])
    high_value = []
    for txn in transactions:
        if txn["amount"] > 100000:
            high_value.append(txn)
    risk_score = len(high_value) / max(len(transactions), 1)
    state["risk_score"] = risk_score
    state["response"] = f"Risk Score: {risk_score:.2f}"
    return state
