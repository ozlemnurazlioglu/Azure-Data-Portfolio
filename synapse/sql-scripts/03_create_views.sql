-- ============================================================
-- STEP 3: Create Analytical Views (Serverless SQL Pool)
-- Optimized views for Power BI consumption
-- ============================================================

-- Denormalized sales view for Power BI DirectQuery
CREATE OR ALTER VIEW sales.vw_sales_denormalized AS
SELECT
    fs.order_id,
    fs.order_date,
    fs.ship_date,
    DATEDIFF(DAY, fs.order_date, fs.ship_date) AS shipping_days,
    dc.customer_id,
    dc.customer_name,
    dc.segment,
    dc.region,
    dc.country,
    dp.product_id,
    dp.product_name,
    dp.category,
    dp.sub_category,
    sr.rep_id,
    sr.rep_name AS sales_rep,
    fs.channel,
    fs.payment_method,
    fs.quantity,
    fs.unit_price,
    fs.discount_pct,
    fs.total_amount,
    fs.cost_amount,
    fs.profit,
    dd.[year],
    dd.[quarter],
    dd.[month],
    dd.month_name,
    dd.fiscal_year,
    dd.fiscal_quarter
FROM sales.fact_sales fs
JOIN sales.dim_customers dc ON fs.customer_id = dc.customer_id
JOIN sales.dim_products dp ON fs.product_id = dp.product_id
JOIN sales.dim_sales_reps sr ON fs.rep_id = sr.rep_id
JOIN sales.dim_date dd ON fs.order_date = dd.full_date;
GO

-- Monthly aggregated view for trend analysis
CREATE OR ALTER VIEW sales.vw_monthly_summary AS
SELECT
    dd.[year],
    dd.[month],
    dd.month_name,
    dd.[quarter],
    dc.region,
    dp.category,
    COUNT(DISTINCT fs.order_id) AS total_orders,
    COUNT(DISTINCT fs.customer_id) AS unique_customers,
    SUM(fs.quantity) AS total_quantity,
    SUM(fs.total_amount) AS total_revenue,
    SUM(fs.cost_amount) AS total_cost,
    SUM(fs.profit) AS total_profit,
    AVG(fs.discount_pct) AS avg_discount,
    SUM(fs.total_amount) / NULLIF(COUNT(DISTINCT fs.order_id), 0) AS avg_order_value
FROM sales.fact_sales fs
JOIN sales.dim_customers dc ON fs.customer_id = dc.customer_id
JOIN sales.dim_products dp ON fs.product_id = dp.product_id
JOIN sales.dim_date dd ON fs.order_date = dd.full_date
GROUP BY dd.[year], dd.[month], dd.month_name, dd.[quarter], dc.region, dp.category;
GO

-- Returns analysis view
CREATE OR ALTER VIEW sales.vw_returns_analysis AS
SELECT
    fr.return_id,
    fr.original_order_id,
    fr.return_date,
    dp.product_name,
    dp.category,
    dp.sub_category,
    fr.quantity AS return_quantity,
    fr.reason AS return_reason,
    fr.refund_amount,
    dd.[year] AS return_year,
    dd.[month] AS return_month
FROM sales.fact_returns fr
JOIN sales.dim_products dp ON fr.product_id = dp.product_id
JOIN sales.dim_date dd ON fr.return_date = dd.full_date;
GO

-- Target vs Actual comparison view
CREATE OR ALTER VIEW sales.vw_target_vs_actual AS
WITH actuals AS (
    SELECT
        dd.[year],
        dd.[month],
        dc.region,
        dp.category,
        SUM(fs.total_amount) AS actual_revenue,
        COUNT(DISTINCT fs.order_id) AS actual_orders
    FROM sales.fact_sales fs
    JOIN sales.dim_customers dc ON fs.customer_id = dc.customer_id
    JOIN sales.dim_products dp ON fs.product_id = dp.product_id
    JOIN sales.dim_date dd ON fs.order_date = dd.full_date
    GROUP BY dd.[year], dd.[month], dc.region, dp.category
)
SELECT
    ft.[year],
    ft.[month],
    ft.region,
    ft.category,
    ft.target_revenue,
    ft.target_orders,
    ISNULL(a.actual_revenue, 0) AS actual_revenue,
    ISNULL(a.actual_orders, 0) AS actual_orders,
    ISNULL(a.actual_revenue, 0) - ft.target_revenue AS revenue_variance,
    CASE
        WHEN ft.target_revenue > 0
        THEN (ISNULL(a.actual_revenue, 0) / ft.target_revenue) * 100
        ELSE 0
    END AS achievement_pct
FROM sales.fact_targets ft
LEFT JOIN actuals a
    ON ft.[year] = a.[year]
    AND ft.[month] = a.[month]
    AND ft.region = a.region
    AND ft.category = a.category;
GO

-- Customer RFM segmentation view
CREATE OR ALTER VIEW sales.vw_customer_rfm AS
WITH customer_metrics AS (
    SELECT
        fs.customer_id,
        dc.customer_name,
        dc.segment,
        dc.region,
        DATEDIFF(DAY, MAX(fs.order_date), CAST('2025-06-30' AS DATE)) AS recency_days,
        COUNT(DISTINCT fs.order_id) AS frequency,
        SUM(fs.total_amount) AS monetary
    FROM sales.fact_sales fs
    JOIN sales.dim_customers dc ON fs.customer_id = dc.customer_id
    GROUP BY fs.customer_id, dc.customer_name, dc.segment, dc.region
),
scored AS (
    SELECT *,
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
        NTILE(5) OVER (ORDER BY monetary ASC) AS m_score
    FROM customer_metrics
)
SELECT *,
    CONCAT(r_score, f_score, m_score) AS rfm_segment,
    CASE
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal Customers'
        WHEN r_score >= 4 AND f_score <= 2 THEN 'New Customers'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
        WHEN r_score <= 2 AND f_score <= 2 THEN 'Lost'
        ELSE 'Potential Loyalists'
    END AS customer_segment_label
FROM scored;
GO
