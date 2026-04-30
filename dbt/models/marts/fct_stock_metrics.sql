{{ config(materialized='table') }}

WITH base AS (
    SELECT *
    FROM {{ ref('stg_stock_prices') }}
),

metrics AS (
    SELECT
    date
    , symbol
    , open
    , high
    , low
    , close
    , volume
    , (close - LAG(close) OVER (PARTITION BY symbol ORDER BY date)) / LAG(close) OVER (PARTITION BY symbol ORDER BY date) AS daily_return
    , AVG(close) OVER (PARTITION BY symbol ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS ma_7
    , AVG(close) OVER (PARTITION BY symbol ORDER BY date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) AS ma_30
    , STDDEV(close) OVER (PARTITION BY symbol ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS volatility_7
    FROM base
)

SELECT * FROM metrics
ORDER BY symbol, date