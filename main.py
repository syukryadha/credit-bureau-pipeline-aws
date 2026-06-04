import logging
import os


from config.config import LOG_FILE, ATHENA_DB, ATHENA_TABLE, ATHENA_S3_PATH, BANK_BUCKET
from extract.read_from_s3 import download_s3_to_temp
from transform.validate import validate_with_pandas
from transform.anonymize import anonymize
from transform.deidentify import deidentify
from load.load_to_athena import load_to_athena
from load.upload_to_s3 import upload_to_s3

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)


def run_pipeline(INBOUND_BUCKET, key, file_bureau_response):
    try:

        temp_filepath = download_s3_to_temp(INBOUND_BUCKET, key)
        valid_rows = validate_with_pandas(temp_filepath)
        anonymized_rows, token_map, loan_map = anonymize(valid_rows)
        processed_rows, count_output_valid_rows = deidentify(
            file_bureau_response, token_map, loan_map)
        with open("final_output.txt", "w") as f:
            f.write("customer_id|credit_score|risk_tier|loan_amount|processed_date\n")
            for row in processed_rows:
                f.write(
                    f"{row.get('customer_id')}|{row.get('credit_score')}|{row.get('risk_tier')}|{row.get('loan_amount')}|{row.get('processed_date')}\n")

        upload_to_s3('final_output.txt', BANK_BUCKET, 'final_output.txt')
        load_to_athena(processed_rows, ATHENA_S3_PATH, ATHENA_DB, ATHENA_TABLE)
        logging.info("Pipeline completed successfully")
        os.remove(temp_filepath)
    except ValueError as e:
        logging.error(f"Validation error: {e}")
    except Exception as e:
        logging.error(f"Pipeline error: {e}")
