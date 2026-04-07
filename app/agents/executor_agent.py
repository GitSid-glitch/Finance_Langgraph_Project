import pandas as pd
import json
from app.llm import llm
from app.state import FinanceState
def execute_plan(df, plan, schema):
    try:
        current = df.copy()
        for step in plan:
            tool = step.get("tool")
            params = step.get("params", {})
            if tool == "groupby":
                cols = params.get("by", [])
                mapped_cols = [schema.get(c, c) for c in cols]

                current = current.groupby(mapped_cols)
            elif tool == "aggregate":
                op = params.get("op", "sum")
                amount_col = schema.get("amount", "amount")

                if isinstance(current, pd.core.groupby.generic.DataFrameGroupBy):
                    if op == "sum":
                        current = current[amount_col].sum().reset_index()
                    elif op == "mean":
                        current = current[amount_col].mean().reset_index()
                else:
                    if op == "sum":
                        current = current[amount_col].sum()
                    elif op == "mean":
                        current = current[amount_col].mean()
            elif tool == "sort":
                ascending = params.get("ascending", True)

                if isinstance(current, pd.DataFrame):
                    amount_col = schema.get("amount", "amount")
                    if amount_col in current.columns:
                        current = current.sort_values(by=amount_col, ascending=ascending)
                    else:
                        current = current.sort_values(by=current.columns[-1], ascending=ascending)

                elif isinstance(current, pd.Series):
                    current = current.sort_values(ascending=ascending)
            elif tool == "select_top":
                n = params.get("n", 1)
                if isinstance(current, pd.DataFrame) and len(current) >= n:
                    current = current.iloc[[n - 1]]
                elif isinstance(current, pd.Series) and len(current) >= n:
                    current = current.iloc[[n - 1]]
            elif tool == "filter":
                col = params.get("column")
                val = params.get("value")
                real_col = schema.get(col, col)
                if real_col in current.columns:
                    current = current[current[real_col] == val]
            else:
                return {"error": f"Unknown tool: {tool}"}
        return current
    except Exception as e:
        return {"error": str(e)}
def executor_agent(state: FinanceState) -> FinanceState:
    transactions = state.get("transactions", [])
    plan = state.get("plan", [])
    schema = state.get("schema", {})
    query = state.get("user_query", "")

    if not transactions:
        state["response"] = "No data available."
        return state
    df = pd.DataFrame(transactions)
    result = execute_plan(df, plan, schema)
    if isinstance(result, dict) and "error" in result:
        state["response"] = f"Execution failed: {result['error']}"
        return state
    try:
        if isinstance(result, pd.DataFrame) and len(result) == 1:
            result_str = json.dumps(result.iloc[0].to_dict(), indent=2)

        elif isinstance(result, pd.Series):
            result_str = result.to_string()

        elif isinstance(result, pd.DataFrame):
            result_str = result.head(10).to_string()

        else:
            result_str = str(result)

    except Exception:
        result_str = str(result)

    state["execution_result"] = result_str
    prompt = f"""
You are a financial analyst.

STRICT RULES:
- Use ONLY the execution result
- DO NOT say "insufficient information"
- DO NOT hallucinate

User query:
{query}

Execution result:
{result_str}

Give a clear, direct answer.
"""

    answer = llm.invoke(prompt).content

    state["response"] = answer

    return state