import csv
import logging
from datetime import date
from dataclasses import dataclass


@dataclass
class DeidentifiedRow:
    customer_id: str
    credit_score: int
    risk_tier: str
    loan_amount: float
    processed_date: str


def deidentify(file_bureau_response: str, token_map: dict[str, str], loan_map: dict[str, float]) -> tuple[list[DeidentifiedRow], int]:
    with open(file_bureau_response, "r") as bureau_response:
        reader = csv.DictReader(bureau_response, delimiter="|")

        count_output_valid_rows = 0
        processed_rows: list[DeidentifiedRow] = []
        for row in reader:
            token = row.get("token")
            if token not in token_map:
                logging.warning(f"Token {token} not found in token map")
                continue
            raw_score = row.get("credit_score")
            if raw_score is None:
                raise ValueError(f"Missing credit_score for token {token}")
            raw_customer_id = token_map.get(token)
            if raw_customer_id is None:
                raise ValueError(f"Missing customer_id for token {token}")
            raw_risk_tier = row.get("risk_tier")
            if raw_risk_tier is None:
                raise ValueError(f"Missing risk_tier for token {token}")
            raw_loan_amount = row.get("loan_amount")
            if raw_loan_amount is None:
                raise ValueError(f"Missing loan_amount for token {token}")
            
            count_output_valid_rows += 1
            processed_rows.append(DeidentifiedRow(
                customer_id=raw_customer_id,
                credit_score=int(raw_score),
                risk_tier=raw_risk_tier,
                loan_amount=float(raw_loan_amount),
                processed_date=str(date.today())
            ))
        
        logging.info(f"Deidentified {len(processed_rows)} rows successfully")
    return processed_rows, count_output_valid_rows
