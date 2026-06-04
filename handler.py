from main import run_pipeline


fake_event = {
    "Records": [
        {
            "s3": {
                "bucket": {"name": "credit-pipeline-inbound-aws-syukry"},
                "object": {"key": "bank_input.csv"}
            }
        }
    ]
}


def lambda_handler(fake_event, context=None):
    bucket_name = fake_event["Records"][0]["s3"]["bucket"]["name"]
    object_key = fake_event["Records"][0]["s3"]["object"]["key"]
    # Your lambda function logic here
    file_bureau_response = r"03-project-aws\bureau_response.txt"

    # Call your pipeline core function
    run_pipeline(bucket_name, object_key, file_bureau_response)


lambda_handler(fake_event, context=None)
