import logging
from google.cloud import storage
import tempfile


def download_gcs_to_temp(bucket_name, key):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(key)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    temp_file.close()
    blob.download_to_filename(temp_file.name)
    logging.info(f"Downloaded file from GCS: gs://{bucket_name}/{key}")
    return temp_file.name
