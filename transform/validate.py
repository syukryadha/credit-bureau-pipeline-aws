import logging
import pandas as pd


def validate_with_pandas(filepath):

    df = pd.read_csv(filepath)

    required_columns = ["customer_id", "name", "ic_number", "loan_amount"]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Schema check failed — missing columns: {missing}")
    logging.info("Schema check passed")

    total_rows = len(df)

    df = df[~df.duplicated(subset=["customer_id"], keep="first")]
    duplicate_drop = total_rows - len(df)  # rows removed by dedup

    after_dedup = len(df)
    df = df.dropna(subset=["name", "ic_number"])
    null_drop = after_dedup - len(df)  # rows removed by null check

    after_null = len(df)
    df = df[df["loan_amount"] > 0]
    loan_amount_negatives = after_null - \
        len(df)  # rows removed by amount check

    df.to_csv("clean_customers.csv", index=False)
    clean_rows = len(df)

    logging.info(f"Total rows :  {total_rows}")
    logging.info(f"Clean rows:  {clean_rows}")
    logging.info(f"Drop due to duplicate : {duplicate_drop}")
    logging.info(f"Drop due to null : {null_drop}")
    logging.info(f"Drop due to negatives : {loan_amount_negatives}")

    return df.to_dict(orient="records")
