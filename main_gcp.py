import logging
import os
from datetime import date

# import what you need
from config.config_gcp import LOG_FILE, dataset_id, table_id, BANK_BUCKET
from extract.read_from_gcs import download_gcs_to_temp
from transform.validate import validate_with_pandas
from transform.anonymize import anonymize
from transform.deidentify import deidentify
from load.load_to_bigquery import load_to_bigquery
from load.upload_to_gcs import upload_to_gcs

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
        logging.info("Pipeline completed successfully")
        os.remove(temp_filepath)
    except ValueError as e:
        logging.error(f"Validation error: {e}")
    except Exception as e:
        logging.error(f"Pipeline error: {e}")
