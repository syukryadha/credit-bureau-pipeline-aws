import logging
from google.cloud import storage


def upload_to_gcs(local_path, bucket_name, key):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(key)
    blob.upload_from_filename(local_path)
    logging.info(f"File {local_path} uploaded to gcs://{bucket_name}/{key}")
