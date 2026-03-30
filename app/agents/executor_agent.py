import json
from app.llm import llm
from app.state import FinanceState
from app.tools.finance_tools import build_risk_report, build_summary, simulate_what_if
def _fmt(value):
    return f"₹{value:,.2f}" if isinstance(value, (int, float)) else str(value)
def _append_trace(state: FinanceState, action: str, observation: str, parameters=None) -> None:
    trace = state.get("trace", [])
    trace.append(
        {
            "step": state.get("step", 0) + 1,
            "action": action,
            "parameters": parameters or {},
            "observation": observation,
        }
    )
    state["trace"] = trace
    state["step"] = state.get("step", 0) + 1
    state["observation"] = observation
def executor_agent(state: FinanceState) -> FinanceState:
    action = state.get("next_action", "qa")
    transactions = state.get("transactions", [])
    parameters = state.get("parameters", {})
    query = state.get("user_query", "")

    if action == "summary":
        s = build_summary(transactions)
        lines = [
            f"Transactions: {s.get('transaction_count', 0)}",
            f"Total amount: {_fmt(s.get('total_amount', 0.0))}",
            f"Average transaction: {_fmt(s.get('average_amount', 0.0))}",
            f"Median transaction: {_fmt(s.get('median_amount', 0.0))}",
            f"Largest transaction: {_fmt(s.get('max_amount', 0.0))}",
        ]
        if s.get("has_type"):
            lines.extend(
                [
                    f"Credit total: {_fmt(s.get('credit_total', 0.0))}",
                    f"Debit total: {_fmt(s.get('debit_total', 0.0))}",
                    f"Profit / net cashflow: {_fmt(s.get('profit', 0.0))}",
                ]
            )
        else:
            lines.append("Profit / net cashflow: insufficient data for credit/debit-based profit.")

        if s.get("top_categories"):
            lines.append("Top categories: " + ", ".join(
                f"{row.get('category', 'Unknown')}({_fmt(row.get('amount', 0.0))})"
                for row in s["top_categories"][:5]
            ))

        observation = "Summary step completed.\n" + "\n".join(lines)
        _append_trace(state, "summary", observation)
        state["done"] = False
        state["response"] = observation
        return state

    if action == "risk":
        report = build_risk_report(transactions)

        lines = [
            f"Risk score: {report.get('risk_score', 0.0):.2f}",
            f"Outlier threshold: {_fmt(report.get('threshold', 0.0))}",
            f"Outlier count: {report.get('outlier_count', 0)}",
        ]

        if report.get("outliers"):
            lines.append(
                "Flagged transactions: "
                + ", ".join(
                    f"{(row.get('category') or row.get('description') or 'row')}({_fmt(row.get('amount', 0.0))})"
                    for row in report["outliers"][:5]
                )
            )

        observation = "Risk step completed.\n" + "\n".join(lines)
        _append_trace(state, "risk", observation)
        state["done"] = False
        state["response"] = observation
        return state

    if action == "what_if":
        result = simulate_what_if(transactions, state.get("operation", "remove_largest"), parameters)

        if "error" in result:
            observation = f"What-if step failed: {result['error']}"
        else:
            observation = json.dumps(result, indent=2, ensure_ascii=False)

        _append_trace(state, "what_if", observation, parameters)
        state["done"] = False
        state["response"] = observation
        return state

    if action == "clarify":
        question = state.get("clarification_question") or "I need a bit more structured data to answer that accurately."
        observation = question
        _append_trace(state, "clarify", observation)
        state["done"] = True
        state["response"] = observation
        return state
    summary = state.get("summary", {})
    trace = state.get("trace", [])
    sample = transactions[:10]

    prompt = f"""
You are a financial analyst.

Use only the facts below.
Do not invent numbers.
If something cannot be determined, say so plainly.

User query:
{query}

Summary:
{json.dumps(summary, ensure_ascii=False, indent=2, default=str)}

Trace so far:
{json.dumps(trace, ensure_ascii=False, indent=2, default=str)}

Sample transactions:
{json.dumps(sample, ensure_ascii=False, indent=2, default=str)}

Write a concise answer.
"""

    answer = llm.invoke(prompt).content
    observation = answer
    _append_trace(state, "qa", observation)
    state["done"] = True
    state["response"] = answer
    return state