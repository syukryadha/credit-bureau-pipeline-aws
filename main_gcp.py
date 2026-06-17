import logging
import os
import pandas as pd
import config.config_gcp as config
from transform.anonymize_gcp import anonymize


# import what you need
from extract.read_from_gcs import download_gcs_to_temp
from load.load_to_bigquery import load_raw_to_bronze


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
    handlers=[
        logging.FileHandler(config.log_file),
        logging.StreamHandler()
    ]
)


def run_pipeline(bucket_name_inbound, key, key_bureau_response):
    try:
        temp_filepath_bank_file = download_gcs_to_temp(
            bucket_name_inbound, key)
        df_bank_file = pd.read_csv(temp_filepath_bank_file)
        temp_filepath_bureau_response = download_gcs_to_temp(
            bucket_name_inbound, key_bureau_response)
        df_bureau_response = pd.read_csv(
            temp_filepath_bureau_response, delimiter='|')
        load_raw_to_bronze(
            df_bank_file, f"{config.gcp_project_id}.{config.dataset_id}.{config.table_id_raw_customers}")
        load_raw_to_bronze(df_bureau_response,
                           f"{config.gcp_project_id}.{config.dataset_id}.{config.table_id_raw_bureau_response}")
        anonymized_rows, token_map = anonymize(df_bank_file)
        
        logging.info("Pipeline completed successfully")
        os.remove(temp_filepath_bank_file)
        os.remove(temp_filepath_bureau_response)
    except ValueError as e:
        logging.error(f"Validation error: {e}")
    except Exception as e:
        logging.error(f"Pipeline error: {e}")

if __name__ == "__main__":
    run_pipeline(
            bucket_name_inbound=config.bucket_name,
            key=config.key,
            key_bureau_response=config.key_bureau_response,
        )
