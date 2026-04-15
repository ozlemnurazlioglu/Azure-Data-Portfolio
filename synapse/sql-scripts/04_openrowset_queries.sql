-- ============================================================
-- STEP 4: OPENROWSET Queries (Serverless SQL - Ad-hoc Analysis)
-- Query files directly without creating external tables
-- ============================================================

-- Query CSV files directly from Data Lake
SELECT TOP 100 *
FROM OPENROWSET(
    BULK 'https://<storage-account>.dfs.core.windows.net/sales-data/raw/fact_sales.csv',
    FORMAT = 'CSV',
    PARSER_VERSION = '2.0',
    HEADER_ROW = TRUE
) AS sales;

-- Query with explicit schema for type safety
SELECT
    order_id,
    CAST(order_date AS DATE) AS order_date,
    customer_id,
    product_id,
    CAST(quantity AS INT) AS quantity,
    CAST(total_amount AS DECIMAL(12,2)) AS total_amount,
    CAST(profit AS DECIMAL(12,2)) AS profit
FROM OPENROWSET(
    BULK 'https://<storage-account>.dfs.core.windows.net/sales-data/raw/fact_sales.csv',
    FORMAT = 'CSV',
    PARSER_VERSION = '2.0',
    HEADER_ROW = TRUE
) WITH (
    order_id        VARCHAR(20),
    order_date      DATE,
    ship_date       DATE,
    customer_id     VARCHAR(20),
    product_id      VARCHAR(20),
    rep_id          VARCHAR(20),
    channel         VARCHAR(30),
    payment_method  VARCHAR(30),
    quantity        INT,
    unit_price      DECIMAL(10,2),
    discount_pct    DECIMAL(5,2),
    total_amount    DECIMAL(12,2),
    cost_amount     DECIMAL(12,2),
    profit          DECIMAL(12,2)
) AS sales
WHERE CAST(order_date AS DATE) >= '2025-01-01';

-- Query Parquet files (after ETL transforms raw CSV → Parquet)
SELECT
    region,
    category,
    YEAR(order_date) AS [year],
    MONTH(order_date) AS [month],
    COUNT(*) AS order_count,
    SUM(total_amount) AS revenue,
    SUM(profit) AS profit,
    AVG(discount_pct) AS avg_discount
FROM OPENROWSET(
    BULK 'https://<storage-account>.dfs.core.windows.net/sales-data/curated/sales_enriched/*.parquet',
    FORMAT = 'PARQUET'
) AS enriched_sales
GROUP BY region, category, YEAR(order_date), MONTH(order_date)
ORDER BY [year], [month], revenue DESC;

-- Query partitioned Parquet data (year/month partitions)
SELECT *
FROM OPENROWSET(
    BULK 'https://<storage-account>.dfs.core.windows.net/sales-data/curated/partitioned/year=*/month=*/*.parquet',
    FORMAT = 'PARQUET'
) AS partitioned_sales
WHERE partitioned_sales.filepath(1) = '2025'
  AND partitioned_sales.filepath(2) = '06';

-- CETAS: Create External Table As Select (materialize transformed data)
CREATE EXTERNAL TABLE sales.curated_monthly_summary
WITH (
    LOCATION = 'curated/monthly_summary/',
    DATA_SOURCE = SalesDataLake,
    FILE_FORMAT = ParquetFormat
)
AS
SELECT
    YEAR(fs.order_date) AS [year],
    MONTH(fs.order_date) AS [month],
    dc.region,
    dp.category,
    COUNT(DISTINCT fs.order_id) AS total_orders,
    SUM(fs.total_amount) AS total_revenue,
    SUM(fs.profit) AS total_profit
FROM sales.fact_sales fs
JOIN sales.dim_customers dc ON fs.customer_id = dc.customer_id
JOIN sales.dim_products dp ON fs.product_id = dp.product_id
GROUP BY YEAR(fs.order_date), MONTH(fs.order_date), dc.region, dp.category;
