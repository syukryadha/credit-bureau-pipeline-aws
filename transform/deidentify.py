import csv
import logging
from datetime import date


def deidentify(file_bureau_response: str, token_map: dict[str, str], loan_map: dict[str, float]) -> tuple[list[dict], int]:
    with open(file_bureau_response, "r") as bureau_response:
        reader = csv.DictReader(bureau_response, delimiter="|")

        count_output_valid_rows = 0
        processed_rows = []
        for row in reader:
            token = row.get("token")
            if token not in token_map:
                logging.warning(f"Token {token} not found in token map")
                continue
            raw_score = row.get("credit_score")
            if raw_score is None:
                raise ValueError(f"Missing credit_score for token {token}")

            row["customer_id"] = token_map.get(token)
            row["loan_amount"] = loan_map.get(row["customer_id"])

            count_output_valid_rows += 1
            processed_rows.append({
                "customer_id": row.get("customer_id"),
                "credit_score": int(raw_score),
                "risk_tier": row.get("risk_tier"),
                "loan_amount": row.get("loan_amount"),
                "processed_date": str(date.today())
            })
        for row in processed_rows:
            if row.get("credit_score") is None:
                raise ValueError(
                    f"Row with customer_id {row.get('customer_id')} has null credit score")
        logging.info(f"Deidentified {len(processed_rows)} rows successfully")
    return processed_rows, count_output_valid_rows
