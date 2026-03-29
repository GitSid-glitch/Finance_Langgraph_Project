from app.state import FinanceState
def transaction_agent(state: FinanceState) -> FinanceState:
    query = state.get("user_query", "").lower()
    transactions = state.get("transactions", [])

    if not transactions:
        state["response"] = "No transaction data available."
        return state

    amounts = [txn["amount"] for txn in transactions]

    total = sum(amounts)
    count = len(amounts)
    avg = total / count if count else 0
    max_txn = max(amounts)
    min_txn = min(amounts)
    if "remove" in query and "largest" in query:
        new_amounts = [a for a in amounts if a != max_txn]

        if not new_amounts:
            state["response"] = "Cannot compute after removing largest transaction."
            return state

        new_avg = sum(new_amounts) / len(new_amounts)

        state["response"] = f"""
Original Average: ₹{avg:.2f}
New Average (without largest transaction ₹{max_txn:.2f}): ₹{new_avg:.2f}
"""
        return state
    elif "trend" in query:
        state["response"] = "Trend analysis requires date information, which is not available."
        return state
    elif "total" in query or "revenue" in query:
        state["response"] = f"Total Revenue: ₹{total:,.2f}"
        return state
    elif "compare" in query:
        state["response"] = f"""
Comparison:
Average Transaction: ₹{avg:.2f}
Highest Transaction: ₹{max_txn:.2f}
Lowest Transaction: ₹{min_txn:.2f}
"""
        return state
    else:
        state["response"] = f"""
Financial Summary:
Total Transactions: {count}
Total Revenue: ₹{total:,.2f}
Average Transaction: ₹{avg:.2f}
Highest Transaction: ₹{max_txn:.2f}
Lowest Transaction: ₹{min_txn:.2f}
"""
        return state