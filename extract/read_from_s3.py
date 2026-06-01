import boto3
import tempfile
import logging
from config.config import REGION

def download_s3_to_temp(bucket, key):
    s3 = boto3.client("s3",region_name=REGION)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    temp_file.close()
    s3.download_file(bucket, key, temp_file.name)
    logging.info(f"Downloaded file from S3: s3://{bucket}/{key} to {temp_file.name}")
    return temp_file.name
   