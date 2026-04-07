import pandas as pd
import numpy as np
def build_summary(transactions, schema):
    import pandas as pd
    df = pd.DataFrame(transactions)
    amount_col = "amount"
    category_col = "category"
    if df.empty or amount_col not in df:
        return {}
    df[amount_col] = pd.to_numeric(df[amount_col], errors="coerce")
    df = df.dropna(subset=[amount_col])
    summary = {
        "total": float(df[amount_col].sum()),
        "average": float(df[amount_col].mean()),
    }
    if category_col in df:
        grouped = df.groupby(category_col)[amount_col].sum().sort_values()
        summary["category_rank"] = grouped.to_dict()
        summary["top_category"] = grouped.idxmax()
    return summary


def build_profile(summary):
    return {
        "transaction_count": summary.get("transaction_count", 0),
        "has_type": summary.get("has_type", False),
        "has_date": summary.get("has_date", False),
        "has_category": summary.get("has_category", False),
        "average_amount": summary.get("average_amount", 0.0),
        "profit_available": "profit" in summary,
    }


def build_risk_report(transactions):
    df = pd.DataFrame(transactions)
    if df.empty:
        return {"risk_score": 0}
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df.dropna()
    avg = df["amount"].mean()
    threshold = avg * 2
    outliers = df[df["amount"] > threshold]
    risk_score = len(outliers) / len(df)
    return {
        "risk_score": float(risk_score),
        "threshold": float(threshold),
        "outliers": outliers.to_dict(orient="records"),
    }

def simulate_what_if(transactions, operation, params):
    df = pd.DataFrame(transactions)
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df.dropna()
    amounts = df["amount"].tolist()
    if operation == "remove_largest":
        max_val = max(amounts)
        new_amounts = [x for x in amounts if x != max_val]
        return {
            "original_avg": sum(amounts) / len(amounts),
            "new_avg": sum(new_amounts) / len(new_amounts),
            "removed": max_val,
        }

    return {}