from typing import Any, Dict, List, TypedDict
class FinanceState(TypedDict, total=False):
    user_query: str
    transactions: List[Dict[str, Any]]
    summary: Dict[str, Any]
    profile: Dict[str, Any]
    next_action: str
    operation: str
    parameters: Dict[str, Any]
    clarification_question: str
    trace: List[Dict[str, Any]]
    step: int
    max_steps: int
    done: bool
    observation: str
    response: str
    memory: List[Dict[str, str]]