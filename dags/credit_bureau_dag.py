"""Airflow DAG for credit bureau data pipeline."""
from airflow.providers.google.cloud.operators.dataform import (
    DataformCreateCompilationResultOperator,
    DataformCreateWorkflowInvocationOperator,
)
from airflow.operators.python import PythonOperator
from airflow import DAG
import pandas as pd
from transform.anonymize_gcp import anonymize
from load.load_to_bigquery import load_raw_to_bronze
from extract.read_from_gcs import download_gcs_to_temp
from datetime import datetime, timedelta
import config.config_gcp as config
import os
import sys
import logging
from google.cloud import storage
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")))


default_args = {
    "owner": "syukry",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "depends_on_past": False,
}


def get_latest_file(bucket_name, prefix):
    client = storage.Client()
    blobs = sorted(
        client.list_blobs(bucket_name, prefix=prefix),
        key=lambda b: b.updated,
        reverse=True
    )
    if not blobs:
        raise FileNotFoundError(
            f"No files found in {bucket_name} with prefix {prefix}")
    return blobs[0].name


def read_gcs_bank_function(**context):
    key = get_latest_file(config.bucket_name, "bank_input")
    temp_path = download_gcs_to_temp(config.bucket_name, key)
    context['ti'].xcom_push(key="bank_temp_path", value=temp_path)


def read_gcs_bureau_response_function(**context):
    key = get_latest_file(config.bucket_name, "bureau_response")
    temp_path = download_gcs_to_temp(config.bucket_name, key)
    context['ti'].xcom_push(key="bureau_response_temp_path", value=temp_path)


def load_bronze_raw_customers_function(**context):
    temp_path = context['ti'].xcom_pull(
        task_ids="read_gcs_bank", key="bank_temp_path")
    df = pd.read_csv(temp_path)
    load_raw_to_bronze(
        df, f"{config.gcp_project_id}.{config.dataset_id}.{config.table_id_raw_customers}")


def load_bronze_raw_bureau_response_function(**context):
    temp_path = context['ti'].xcom_pull(
        task_ids="read_gcs_bureau_response", key="bureau_response_temp_path")
    df = pd.read_csv(temp_path, delimiter='|')
    load_raw_to_bronze(
        df, f"{config.gcp_project_id}.{config.dataset_id}.{config.table_id_raw_bureau_response}")


def anonymize_data_function(**context):
    temp_path = context['ti'].xcom_pull(
        task_ids="read_gcs_bank", key="bank_temp_path")
    df = pd.read_csv(temp_path)
    anonymized_rows, token_map = anonymize(df)
    context['ti'].xcom_push(key="token_map", value=token_map)


def write_output_function(**context):
    # Gold marts in BigQuery are the pipeline output.
    # future: export fact_processed_customers to GCS if downstream needs flat file.
    logging.info("Gold marts in BigQuery are the pipeline output.")


with DAG(
    dag_id="credit_bureau_dag",
    default_args=default_args,
    start_date=datetime(2026, 6, 15),
    schedule_interval=None,
    catchup=False,
) as dag:
    read_gcs_bank = PythonOperator(
        task_id="read_gcs_bank",
        python_callable=read_gcs_bank_function,
        retries=2,
    )
    read_gcs_bureau_response = PythonOperator(
        task_id="read_gcs_bureau_response",
        python_callable=read_gcs_bureau_response_function,
        retries=2,
    )
    anonymize_data = PythonOperator(
        task_id="anonymize_data",
        python_callable=anonymize_data_function,
    )
    load_bronze_raw_customers = PythonOperator(
        task_id="load_bronze_raw_customers",
        python_callable=load_bronze_raw_customers_function,
    )
    load_bronze_raw_bureau_response = PythonOperator(
        task_id="load_bronze_raw_bureau_response",
        python_callable=load_bronze_raw_bureau_response_function,
    )

    dataform_compile_silver = DataformCreateCompilationResultOperator(
        task_id="dataform_compile_silver",
        project_id=config.project_id,
        region=config.region,
        repository_id=config.repository_id,
        compilation_result={
            "git_commitish": "main",
            "workspace": config.workspace_name,
        },
    )

    dataform_run_silver = DataformCreateWorkflowInvocationOperator(
        task_id="dataform_run_silver",
        project_id=config.project_id,
        region=config.region,
        repository_id=config.repository_id,
        workflow_invocation={
            "compilation_result": "{{ task_instance.xcom_pull('dataform_compile_silver')['name']}}",
            "invocation_config": {
                "included_tags": ["silver"],
            },
        },
    )

    dataform_compile_gold = DataformCreateCompilationResultOperator(
        task_id="dataform_compile_gold",
        project_id=config.project_id,
        region=config.region,
        repository_id=config.repository_id,
        compilation_result={
            "git_commitish": "main",
            "workspace": config.workspace_name,
        },
    )

    dataform_run_gold = DataformCreateWorkflowInvocationOperator(
        task_id="dataform_run_gold",
        project_id=config.project_id,
        region=config.region,
        repository_id=config.repository_id,
        workflow_invocation={
            "compilation_result": "{{ task_instance.xcom_pull('dataform_compile_gold')['name']}}",
            "invocation_config": {
                "included_tags": ["gold"],
            },
        },
    )

    write_output = PythonOperator(
        task_id="write_output",
        python_callable=write_output_function,
    )

    read_gcs_bank >> anonymize_data
    read_gcs_bank >> load_bronze_raw_customers
    read_gcs_bureau_response >> load_bronze_raw_bureau_response
    [load_bronze_raw_customers, load_bronze_raw_bureau_response,
        anonymize_data] >> dataform_compile_silver >> dataform_run_silver >> dataform_compile_gold >> dataform_run_gold >> write_output
