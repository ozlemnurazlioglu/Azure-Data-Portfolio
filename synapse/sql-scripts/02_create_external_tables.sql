-- ============================================================
-- STEP 2: Create External Tables (Serverless SQL Pool)
-- Reads directly from Data Lake without loading into memory
-- ============================================================

CREATE SCHEMA IF NOT EXISTS sales;
GO

-- Dimension: Products
CREATE EXTERNAL TABLE sales.dim_products (
    product_id      VARCHAR(20),
    product_name    VARCHAR(100),
    category        VARCHAR(50),
    sub_category    VARCHAR(50),
    unit_price      DECIMAL(10, 2),
    unit_cost       DECIMAL(10, 2)
)
WITH (
    LOCATION = 'raw/dim_products.csv',
    DATA_SOURCE = SalesDataLake,
    FILE_FORMAT = CsvFormat
);

-- Dimension: Customers
CREATE EXTERNAL TABLE sales.dim_customers (
    customer_id     VARCHAR(20),
    customer_name   VARCHAR(100),
    segment         VARCHAR(50),
    region          VARCHAR(50),
    country         VARCHAR(50)
)
WITH (
    LOCATION = 'raw/dim_customers.csv',
    DATA_SOURCE = SalesDataLake,
    FILE_FORMAT = CsvFormat
);

-- Dimension: Sales Reps
CREATE EXTERNAL TABLE sales.dim_sales_reps (
    rep_id      VARCHAR(20),
    rep_name    VARCHAR(100),
    region      VARCHAR(50)
)
WITH (
    LOCATION = 'raw/dim_sales_reps.csv',
    DATA_SOURCE = SalesDataLake,
    FILE_FORMAT = CsvFormat
);

-- Dimension: Date
CREATE EXTERNAL TABLE sales.dim_date (
    date_key        INT,
    full_date       DATE,
    [year]          INT,
    [quarter]       VARCHAR(5),
    [month]         INT,
    month_name      VARCHAR(20),
    day_of_week     VARCHAR(20),
    is_weekend      BIT,
    fiscal_year     VARCHAR(10),
    fiscal_quarter  VARCHAR(10)
)
WITH (
    LOCATION = 'raw/dim_date.csv',
    DATA_SOURCE = SalesDataLake,
    FILE_FORMAT = CsvFormat
);

-- Fact: Sales
CREATE EXTERNAL TABLE sales.fact_sales (
    order_id        VARCHAR(20),
    order_date      DATE,
    ship_date       DATE,
    customer_id     VARCHAR(20),
    product_id      VARCHAR(20),
    rep_id          VARCHAR(20),
    channel         VARCHAR(30),
    payment_method  VARCHAR(30),
    quantity        INT,
    unit_price      DECIMAL(10, 2),
    discount_pct    DECIMAL(5, 2),
    total_amount    DECIMAL(12, 2),
    cost_amount     DECIMAL(12, 2),
    profit          DECIMAL(12, 2)
)
WITH (
    LOCATION = 'raw/fact_sales.csv',
    DATA_SOURCE = SalesDataLake,
    FILE_FORMAT = CsvFormat
);

-- Fact: Returns
CREATE EXTERNAL TABLE sales.fact_returns (
    return_id           VARCHAR(20),
    original_order_id   VARCHAR(20),
    return_date         DATE,
    product_id          VARCHAR(20),
    quantity            INT,
    reason              VARCHAR(50),
    refund_amount       DECIMAL(12, 2)
)
WITH (
    LOCATION = 'raw/fact_returns.csv',
    DATA_SOURCE = SalesDataLake,
    FILE_FORMAT = CsvFormat
);

-- Fact: Targets
CREATE EXTERNAL TABLE sales.fact_targets (
    [year]          INT,
    [month]         INT,
    region          VARCHAR(50),
    category        VARCHAR(50),
    target_revenue  DECIMAL(12, 2),
    target_orders   INT
)
WITH (
    LOCATION = 'raw/fact_targets.csv',
    DATA_SOURCE = SalesDataLake,
    FILE_FORMAT = CsvFormat
);
