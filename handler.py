from main import run_pipeline


def lambda_handler(event, context=None):
    bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
    object_key = event["Records"][0]["s3"]["object"]["key"]
    file_bureau_response = "bureau_response.txt"

    run_pipeline(bucket_name, object_key, file_bureau_response)