{{ config(materialized='view') }}

SELECT
    DATE(date) AS date,
    symbol,
    CAST(open AS FLOAT64) AS open,
    CAST(high AS FLOAT64) AS high,
    CAST(low AS FLOAT64) AS low,
    CAST(close AS FLOAT64) AS close,
    CAST(volume AS INT64) AS volume
FROM `stock-market-analytics-492503.stock_data.clean_stock_prices`