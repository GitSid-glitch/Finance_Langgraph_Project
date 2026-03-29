from app.state import FinanceState
def risk_agent(state: FinanceState) -> FinanceState:
    transactions = state.get("transactions", [])
    if not transactions:
        state["response"] = "No transaction data available."
        return state
    amounts = [txn["amount"] for txn in transactions]
    avg = sum(amounts) / len(amounts)
    threshold = 2 * avg
    high_value = [txn for txn in transactions if txn["amount"] > threshold]
    risk_score = len(high_value) / len(transactions)

    state["risk_score"] = risk_score

    state["response"] = f"""
Risk Analysis:

Risk Score: {risk_score:.2f}
Threshold: ₹{threshold:.2f}

High-risk Transactions: {len(high_value)}

Reason:
Transactions exceeding 2× average spending are flagged as potential risks.
"""
    return state