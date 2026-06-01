import boto3
from config.config import REGION
import logging

def upload_to_s3(file_path,bucket_name, object_name):
    s3 = boto3.client('s3',region_name=REGION)
    s3.upload_file(file_path, bucket_name, object_name)
    logging.info(f"File {file_path} uploaded to s3://{bucket_name}/{object_name}")