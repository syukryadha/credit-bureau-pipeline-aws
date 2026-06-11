import logging
import pandas as pd
import config.config_gcp as config

temp_filepath_bank_file = download_gcs_to_temp(
            bucket_name_inbound, key)
        df_bank_file = pd.read_csv(temp_filepath_bank_file)

def anonymize(valid_rows: pd.DataFrame) -> tuple[list[dict], dict[str, str]]:
    """token_map is a dictionary where the key is the tokenized customer_id and the value is the original customer_id.
    For example, if the original customer_id is "C001", the token would be "TKN-001". This way, we can easily reverse the token back to the original customer_id when needed.
    customer_id is tokenized by replacing the first character with "TKN-" and keeping the rest of the characters the same. This is a simple way to anonymize the customer_id while still allowing us to reverse it back to the original value when needed.
    token_map generated from valid_rows, which is df_bank_file
    """
    token_map = {"TKN-" + row["customer_id"][1:]: row["customer_id"] for index, row in valid_rows.iterrows()}
    reversed_map = {v: k for k, v in token_map.items()}
    
    


    anonymized_rows = []
    for index, row in valid_rows.iterrows():
        token = reversed_map[row["customer_id"]]
        anonymized_rows.append(
            {"token": token, "loan_amount": row["loan_amount"]})

    with open("bureau_request.txt", "w") as output:
        print("token|loan_amount", file=output)
        for row in anonymized_rows:
            print(f"{row.get('token')}|{row.get('loan_amount')}", file=output)
    
    # Write token_map to BigQuery bronze layer
    token_map_rows = [{"token": token, "customer_id": customer_id} for token, customer_id in token_map.items()]
    df_token_map = pd.DataFrame(token_map_rows)
    # table_id = "TODO(human)"  # format: project_id.dataset.table
    table_id = f"{config.gcp_project_id}.{config.dataset_id}.{config.table_id_token_map}"
    df_token_map.to_gbq(table_id, project_id=config.gcp_project_id, if_exists="append")

    logging.info(f"Anonymized {len(anonymized_rows)} rows")
    logging.info(f"Token map written to BigQuery")

    return anonymized_rows, token_map

