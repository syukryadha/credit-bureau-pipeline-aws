import logging
import os
import pandas as pd
from config.config_gcp import GCP_PROJECT_ID


# import what you need
from config.config_gcp import LOG_FILE
from extract.read_from_gcs import download_gcs_to_temp
from load.load_to_bigquery import load_raw_to_bronze


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)


def run_pipeline(bucket_name, key, file_bureau_response):
    try:
        """
        temp_filepath = download_gcs_to_temp(bucket_name, key)
        valid_rows = validate_with_pandas(temp_filepath)
        anonymized_rows, token_map, loan_map = anonymize(valid_rows)
        processed_rows, count_output_valid_rows = deidentify(
            file_bureau_response, token_map, loan_map)
        with open("final_output.txt", "w") as f:
            f.write("customer_id|credit_score|risk_tier|loan_amount|processed_date\n")
            for row in processed_rows:
                f.write(
                    f"{row.get('customer_id')}|{row.get('credit_score')}|{row.get('risk_tier')}|{row.get('loan_amount')}|{row.get('processed_date')}\n")

        upload_to_gcs('final_output.txt', BANK_BUCKET, 'final_output.txt')
        load_to_bigquery(processed_rows, dataset_id, table_id)
        """
        temp_filepath_bank_file = download_gcs_to_temp(
            bucket_name_inbound, key)
        df_bank_file = pd.read_csv(temp_filepath_bank_file)
        temp_filepath_bureau_response = download_gcs_to_temp(
            bucket_name_inbound, key_bureau_response)
        df_bureau_response = pd.read_csv(
            temp_filepath_bureau_response, delimiter='|')
        load_raw_to_bronze(
            df_bank_file, f"{GCP_PROJECT_ID}.bronze.raw_customers")
        load_raw_to_bronze(df_bureau_response,
                           f"{GCP_PROJECT_ID}.bronze.raw_bureau_response")
        logging.info("Pipeline completed successfully")
        os.remove(temp_filepath_bank_file)
        os.remove(temp_filepath_bureau_response)
    except ValueError as e:
        logging.error(f"Validation error: {e}")
    except Exception as e:
        logging.error(f"Pipeline error: {e}")
