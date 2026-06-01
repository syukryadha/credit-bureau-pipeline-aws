from main_gcp import run_pipeline
from config.config_gcp import bucket_name


file_bureau_response = r"03-project-aws\bureau_response.txt"
key = "bank_input.csv"
run_pipeline(bucket_name, key, file_bureau_response)
