import json
from typing import Any, Dict
from app.llm import llm
from app.state import FinanceState
def _extract_json(text: str) -> Dict[str, Any]:
    text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return {}
    try:
        return json.loads(text[start : end + 1])
    except Exception:
        return {}
def planner_agent(state: FinanceState) -> FinanceState:
    query = state.get("user_query", "")
    profile = state.get("profile", {})
    trace = state.get("trace", [])

    last_action = trace[-1]["action"] if trace else None

    prompt = f"""
You are the planner in a financial reasoning graph.

Return JSON only. No markdown. No extra text.

Choose exactly one next_action:
summary, risk, what_if, qa, clarify, final

Use these rules:
- summary: totals, spending, profit, income, expense, category breakdown, trend
- risk: suspicious, fraud, anomalous, unusual, outlier, suspicious activity
- what_if: remove, reduce, compare after change, simulate, what happens if
- qa: give a grounded answer using the available facts
- clarify: important data is missing
- final: you already have enough evidence from prior tool outputs

Do not repeat the same tool action twice unless new evidence clearly justifies it.
Prefer a short chain of at most 3 tool calls.

Available profile:
{json.dumps(profile, ensure_ascii=False, indent=2)}

Previous trace:
{json.dumps(trace, ensure_ascii=False, indent=2)}

User query:
{query}

Return schema:
{{
  "next_action": "summary|risk|what_if|qa|clarify|final",
  "operation": "remove_largest|remove_top_n|reduce_largest_percent|compare_average_vs_highest|compare_after_removal|none",
  "parameters": {{}},
  "clarification_question": "only if clarify",
  "why": "short reason"
}}
"""

    raw = llm.invoke(prompt).content
    data = _extract_json(raw)

    next_action = data.get("next_action", "qa")
    operation = data.get("operation", "none")
    parameters = data.get("parameters", {})
    clarification_question = data.get("clarification_question", "")

    if next_action not in {"summary", "risk", "what_if", "qa", "clarify", "final"}:
        next_action = "qa"

    if next_action == last_action and next_action in {"summary", "risk", "what_if"}:
        next_action = "final"

    state["next_action"] = next_action
    state["operation"] = operation
    state["parameters"] = parameters if isinstance(parameters, dict) else {}
    state["clarification_question"] = clarification_question

    return state