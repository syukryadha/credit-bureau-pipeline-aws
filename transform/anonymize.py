import logging


def anonymize(valid_rows):
    token_map = {"TKN-" + row["customer_id"][1:]                 : row["customer_id"] for row in valid_rows}
    reversed_map = {v: k for k, v in token_map.items()}
    loan_map = {row["customer_id"]: row["loan_amount"] for row in valid_rows}

    anonymized_rows = []
    for row in valid_rows:
        token = reversed_map[row["customer_id"]]
        anonymized_rows.append(
            {"token": token, "loan_amount": row["loan_amount"]})

    with open("bureau_request.txt", "w") as output:
        print("token|loan_amount", file=output)
        for row in anonymized_rows:
            print(f"{row.get('token')}|{row.get('loan_amount')}", file=output)

    logging.info(f"Anonymized {len(anonymized_rows)} rows")

    return anonymized_rows, token_map, loan_map
