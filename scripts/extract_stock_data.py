import requests
import time
import pandas as pd
from google.cloud import bigquery

api_key = "XBBRS5X68COYUUVL"
symbols = ["SPY", "QQQ"]


def fetch_stock_data(symbols):
    url = f"https://www.alphavantage.co/query"

    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbols,
        "apikey": api_key
    }

    response = requests.get(url, params=params)
    data = response.json()

    return data


def transform_data(raw_data, symbol):
    time_series = raw_data["Time Series (Daily)"]

    df = pd.DataFrame.from_dict(time_series, orient="index")
    df.reset_index(inplace=True)

    df.rename(columns={
        "index": "date",
        "1. open": "open",
        "2. high": "high",
        "3. low": "low",
        "4. close": "close",
        "5. volume": "volume"
    }, inplace=True)

    df["date"] = pd.to_datetime(df["date"])
    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(int)
    df["symbol"] = symbol

    return df


def load_to_bigquery(df):
    client = bigquery.Client()

    table_id = "stock-market-analytics-492503.stock_data.raw_stock_prices"

    job_config = bigquery.LoadJobConfig(
        schema=[
            bigquery.SchemaField("date", "DATE"),
            bigquery.SchemaField("open", "FLOAT"),
            bigquery.SchemaField("high", "FLOAT"),
            bigquery.SchemaField("low", "FLOAT"),
            bigquery.SchemaField("close", "FLOAT"),
            bigquery.SchemaField("volume", "INTEGER"),
            bigquery.SchemaField("symbol", "STRING"),
        ],
        write_disposition="WRITE_APPEND"
    )

    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()

    print("Data loaded successfully.")


if __name__ == "__main__":
    final_df = pd.DataFrame()

    for symbol in symbols:
        print(f"Adding {symbol}")

        raw_data = fetch_stock_data(symbol)

        if "Time Series (Daily)" not in raw_data:
            print(f"Error fetching {symbol}")
            continue

        print(symbol)

        df = transform_data(raw_data, symbol)
        final_df = pd.concat([final_df, df], ignore_index=True)

        time.sleep(12)
    if not final_df.empty:
        load_to_bigquery(final_df)
    else:
        print("No data.")
