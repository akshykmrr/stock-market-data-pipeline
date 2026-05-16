## STOCK MARKET ANALYTICS PIPELINE ##

# Purpose:

The purpose of the project is to build a fully automated pipeline that ingests financial market data for ETF performance analysis.
The dashboard is designed to provide a consolidated view of ETF behavior by combining price trends, volatility analysis, momentum 
indicators, and trading activity into a single analytics interface.

ETFs observed:
1. QQQ — Invesco QQQ Trust (Nasdaq-100)
2. SPY — SPDR S&P 500 ETF Trust

The pipeline ingests daily market data, cleans and standardizes it, calculates analytical metrics and visualizes the results through a Power BI dashboard.

It solves the below points:
- Automating daily market data ingestion
- Cleaning and deduplication of data
- Enabling visual comparison between QQQ and SPY
- Readily providing datasets for reporting

The final solution provides a workflow that monitors:
- Price movement
- Daily returns
- Daily Volume changes
- Moving averages (using 7-day and 30-day averages)
- Market volatility (7-day calculation)

# Pipeline

Phase 1 - Data Ingestion

DAG set up in Airflow is run on a daily schedule. It triggers the below processes:
1. Python Script for ETL that fetches stock data for 'QQQ' and 'SPY' ETFs from Alpha Vantage using an API, performs initial transformation like column header normalization, 
datatype consistency and loads raw data into a reference table in BigQuery.
2. A following task is set up to remove any duplicate records (keep already existing data and remove duplicate data from each run) and stores it in one more reference table.

Phase 2 - dbt Transformations

Data transformation is conducted using 2 layers of dbt transformation:
1. Staging Layer. Further column standardization, datatype conversion is done here to produce a clean, readable structure.
2. Marts Layer. Data from staging layer is ingested to calculate daily returns, 7 day moving average, 30 day moving average and 7 day volatility numbers.
3. Final data is loaded into the facts table, which is ready to be sourced into Power BI for viz.

Phase 3 - Data Visualization

Following charts and cards are used to visualize ingested data for overall analysis of how the ETFs perform:
1. Daily Price Movement (Open vs Close). A line chart is used to track daily open and close prices for both 'QQQ' and 'SPY', segregated on the ETF level.
2. Market Day close price. Final price at which the ETF was closed on the latest market day.
3. Day-over-Day Return. The 'daily return' calculation is used to obtain the percentage of change in close price between the current market day and the previous market day.
4. 4w Average High. The average high price is calculated for a 28 day rolling window (or 4 weeks) on and before the current market day.
5. 4w Average Low. The average low price is calculated for a 28 day rolling window (or 4 weeks) on and before the current market day.
6. Daily Volume Change. The total increase or decrease in volume, along with the percentage difference, is calculated between the current market day and previous market day.
7. Mean Volatility (by date). It depicts how much the ETF price fluctuates over time. Higher value means larger price swings and lower value means a more stable movement in price.
8. Volatility Distribution. It shows how frequently the volatility falls within a certain range. It gives an idea of the ETF's overall volatility behaviour.
9. Moving Average Gap (by date). It is the difference between the short-term (7-days) moving average and long-term (30-days) moving average. When the line is above 0, short term 
momentum is stronger - bullish behaviour. When line is below 0, short term momentum is weaker  - bearish behaviour. When it just crosses 0, it is known as the Golden Cross (good 
time to invest).

# Dashboard Access

The Power BI dashboard is available in this path: stock-market-data-pipeline\dashboard\stock-market-analytics.pbix

# Security Notes

The following files are excluded from GitHub using '.gitignore':
1. Service Account credentials
2. Alpha Vantage API Key
3. Virtual environments
4. Cache files