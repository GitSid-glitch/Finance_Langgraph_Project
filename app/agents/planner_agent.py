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
        return json.loads(text[start:end + 1])
    except Exception:
        return {}
def planner_agent(state: FinanceState) -> FinanceState:
    query = state.get("user_query", "")
    schema = state.get("schema", {})
    prompt = f"""
You are a financial data planner.

Return ONLY valid JSON.

Your job:
Convert the user query into a sequence of data operations.

Available tools:

1. groupby → {{"by": ["column"]}}
2. aggregate → {{"op": "sum" | "mean"}}
3. sort → {{"ascending": true | false}}
4. select_top → {{"n": number}}
5. filter → {{"column": "...", "value": "..."}}

IMPORTANT RULES:
- Use ONLY columns from schema
- "amount" is the metric column
- "select_top n=5" means return ONLY the 5th element (NOT top 5)
- Keep plan minimal and logical

Schema:
{json.dumps(schema, indent=2)}

User query:
{query}

Return format:
{{
  "plan": [
    {{"tool": "groupby", "params": {{...}}}}
  ]
}}
"""
    raw = llm.invoke(prompt).content
    data = _extract_json(raw)
    plan = data.get("plan", [])
    if not isinstance(plan, list) or not plan:
        plan = [
            {"tool": "aggregate", "params": {"op": "sum"}}
        ]
    state["plan"] = plan
    return state