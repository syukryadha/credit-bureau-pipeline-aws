import awswrangler as wr
import pandas as pd
import logging


def load_to_athena(processed_rows, s3_path, database, table):
    df = pd.DataFrame(processed_rows)

    wr.s3.to_parquet(
        df=df,
        path=s3_path,
        dataset=True,
        database=database,
        table=table,
        mode="overwrite"
    )
    logging.info(f"Loaded {len(df)} rows to Athena table: {database}.{table}")
