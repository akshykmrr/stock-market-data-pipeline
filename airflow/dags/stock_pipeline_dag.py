from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from datetime import datetime
import sys
import pandas as pd
import time

sys.path.append("/mnt/c/Users/foxho/OneDrive/Documents/Docs/Projects/stock-market-analysis/scripts")

from extract_stock_data import fetch_stock_data, transform_data, load_to_bigquery

def run_pipeline():
    symbols = ["SPY", "QQQ"]
    final_df = pd.DataFrame()
    for symbol in symbols:
        print(f"Processing {symbol}")
        raw_data = fetch_stock_data(symbol)
        if "Time Series (Daily)" not in raw_data:
	        print(f"Error fetching {symbol}")
	        continue
        df = transform_data(raw_data, symbol)
        final_df = pd.concat([final_df,df], ignore_index=True)
        time.sleep(12)

    if not final_df.empty:
       load_to_bigquery(final_df)
    else:
       print("No data")

default_args = {
    "owner": "airflow",
               }

with DAG(
    dag_id="stock_data_pipeline",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
) as dag:

    run_etl = PythonOperator(
        task_id="run_stock_etl",
        python_callable=run_pipeline,
    )
    deduplicate_data = BigQueryInsertJobOperator(
        task_id="deduplicate_data",
        configuration={
	       "query":{
                      "query":"""
                             CREATE OR REPLACE TABLE `stock-market-analytics-492503.stock_data.clean_stock_prices`
                                        PARTITION BY(date) CLUSTER BY symbol AS
                                        SELECT
                                        date
                                        , open
                                        , high
                                        , low
                                        , close
                                        , volume
                                        , symbol
                                        FROM (
                                              SELECT *
                                              , ROW_NUMBER() OVER(PARTITION BY date, symbol ORDER BY date DESC) AS row_number
                                              FROM `stock-market-analytics-492503.stock_data.raw_stock_prices`
  					      )
                                        WHERE row_number = 1
					""",
                                        "useLegacySQL":False,
			 }
		       },
                                             )

    run_etl >> deduplicate_data
