from google.cloud import bigquery
import logging

def load_to_bigquery(processed_rows,dataset_id,table_id):
    bq_client = bigquery.Client()
    table_ref = (f"{dataset_id}.{table_id}")

    bq_client.insert_rows_json(
        table_ref,
        processed_rows

    )
    

    logging.info(f"Loaded {len(processed_rows)} into Bigquery table_ref :{dataset_id}.{table_id}")