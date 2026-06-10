"""Load data into BigQuery tables."""

from google.cloud import bigquery
import logging
import pandas as pd

# load raw to bronze layer in bigquery
def load_raw_to_bronze(df: pd.DataFrame, table_id: str) -> None:
    # Load the DataFrame to BigQuery
    try:
        bq_client = bigquery.Client()
        # table_id format: "project_id.dataset_id.table_id"
        # bigquery.LoadJobConfig() can be used to specify additional options for the load job, such as the write disposition, schema, etc.
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND)
        job = bq_client.load_table_from_dataframe(
            df, table_id, job_config=job_config)
        job.result()  # Wait for the job to complete
        logging.info(f"Loaded {len(df)} rows into BigQuery table {table_id}")
    except Exception as e:
        logging.error(f"Error occurred while loading data to BigQuery: {e}")
