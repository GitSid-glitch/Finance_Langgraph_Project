import json
from app.graph import build_graph
with open("data/sample_transactions.json") as trn:
    transactions = json.load(trn)
app = build_graph()
state = {
    "user_query": "Check risk in my transactions",
    "intent": "",
    "transactions": transactions,
    "risk_score": 0.0,
    "response": "",
    "memory": []
}
final_state = app.invoke(state)
print("\n=== FINAL RESPONSE ===")
print(final_state["response"])
