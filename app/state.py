from typing import TypedDict, List, Dict
class FinanceState(TypedDict):
    user_query: str
    intent: str
    transactions: List[Dict]
    risk_score: float
    response: str
    memory: List[str]
