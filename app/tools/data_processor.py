import json
import pandas as pd
import pdfplumber
def clean_amount(value):
    try:
        return float(
            str(value)
            .replace("₹", "")
            .replace("$", "")
            .replace(",", "")
            .strip()
        )
    except:
        return None
def convert_possible_numeric(df):
    for col in df.columns:
        df[col] = df[col].astype(str)
        df[col] = df[col].str.replace(",", "")
        df[col] = df[col].str.replace("₹", "").str.replace("$", "")
        try:
            df[col] = pd.to_numeric(df[col])
        except:
            continue

    return df
def detect_schema(df):
    mapping = {}
    for col in df.columns:
        c = col.lower()
        if "amount" not in mapping and any(k in c for k in ["amount", "price", "value", "revenue", "sales"]):
            mapping["amount"] = col
        elif "category" not in mapping and any(k in c for k in ["category", "type", "product"]):
            mapping["category"] = col
        elif "region" not in mapping and any(k in c for k in ["region", "location", "city", "area"]):
            mapping["region"] = col
        elif "date" not in mapping and ("date" in c or "time" in c):
            mapping["date"] = col
    return mapping
def handle_debit_credit(df):
    cols = df.columns
    if "debit" in cols and "credit" in cols:
        df["amount"] = df["credit"].fillna(0) - df["debit"].fillna(0)
        return df, "amount"
    return df, None
def guess_amount_column(df):
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if not numeric_cols:
        return None
    col_scores = {}
    for col in numeric_cols:
        col_scores[col] = df[col].abs().mean()
    return max(col_scores, key=col_scores.get)
def dataframe_to_transactions(df):
    if df is None or df.empty:
        return [], {}
    df = df.dropna(how="all")
    df.columns = df.columns.str.strip().str.lower()

    schema = detect_schema(df)

    df = convert_possible_numeric(df)

    df, amount_col = handle_debit_credit(df)
    if amount_col is None:
        amount_col = schema.get("amount")
    if amount_col is None:
        amount_col = guess_amount_column(df)

    if amount_col is None:
        return [], schema

    transactions = []

    category_col = schema.get("category")
    date_col = schema.get("date")
    region_col = schema.get("region")

    for _, row in df.iterrows():
        value = row.get(amount_col)

        if pd.isna(value):
            continue

        amount = clean_amount(value)
        if amount is None:
            continue

        txn = {"amount": amount}

        if category_col and category_col in row:
            txn["category"] = str(row[category_col])

        if date_col and date_col in row:
            txn["date"] = str(row[date_col])

        if region_col and region_col in row:
            txn["region"] = str(row[region_col])
        for col in df.columns:
            if any(k in col for k in ["desc", "note", "narration"]):
                val = row.get(col)
                if pd.notna(val):
                    txn["description"] = str(val)

        transactions.append(txn)

    return transactions, schema

def parse_pdf(uploaded_file):
    transactions = []

    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()

            for table in tables:
                if len(table) < 2:
                    continue

                df = pd.DataFrame(table[1:], columns=table[0])
                txns, _ = dataframe_to_transactions(df)
                transactions.extend(txns)

            text = page.extract_text()

            if text:
                for word in text.split():
                    amt = clean_amount(word)
                    if amt:
                        transactions.append({"amount": amt})

    return transactions, {}
def parse_file(uploaded_file):
    file_name = uploaded_file.name.lower()

    # JSON
    if file_name.endswith(".json"):
        data = json.load(uploaded_file)
        df = pd.DataFrame(data)
        return dataframe_to_transactions(df)

    # CSV
    elif file_name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
        return dataframe_to_transactions(df)

    # Excel
    elif file_name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)
        return dataframe_to_transactions(df)

    # PDF
    elif file_name.endswith(".pdf"):
        return parse_pdf(uploaded_file)

    else:
        raise ValueError("Unsupported file format")