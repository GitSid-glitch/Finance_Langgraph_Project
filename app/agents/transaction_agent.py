from app.state import FinanceState
def transaction_agent(state: FinanceState) -> FinanceState:
    transactions = state.get("transactions", [])
    total = 0
    for txn in transactions:
        total += txn["amount"]
    count = len(transactions)
    state["response"] = (f"Transaction Summary:\n" f"Total Transactions: {count}\n" f"Total Amount: ₹{total}")
    return state
