import awswrangler as wr
import pandas as pd
import logging
from typing import Any


def load_to_athena(processed_rows: list[dict[str, Any]], s3_path: str, database: str, table: str) -> None:
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
