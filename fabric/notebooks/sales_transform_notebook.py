# Fabric Notebook: Sales Data Transformation (Medallion Architecture)
# Runtime: Fabric Spark (PySpark)
# Lakehouse: SalesLakehouse

# %% [markdown]
# # Sales Data Pipeline — Medallion Architecture
# Bronze (raw CSV) → Silver (cleaned Parquet) → Gold (curated Delta tables)

# %% Bronze Layer — Ingest raw CSV files from OneLake

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType,
    DoubleType, DateType
)

spark = SparkSession.builder.getOrCreate()

LAKEHOUSE_PATH = "abfss://SalesAnalytics_WS@onelake.dfs.fabric.microsoft.com/SalesLakehouse.Lakehouse"
RAW_PATH = f"{LAKEHOUSE_PATH}/Files/raw"
STAGING_PATH = f"{LAKEHOUSE_PATH}/Files/staging"

dim_customers_raw = spark.read.option("header", True).csv(f"{RAW_PATH}/dim_customers.csv")
dim_products_raw = spark.read.option("header", True).csv(f"{RAW_PATH}/dim_products.csv")
dim_date_raw = spark.read.option("header", True).csv(f"{RAW_PATH}/dim_date.csv")
dim_sales_reps_raw = spark.read.option("header", True).csv(f"{RAW_PATH}/dim_sales_reps.csv")
fact_sales_raw = spark.read.option("header", True).csv(f"{RAW_PATH}/fact_sales.csv")
fact_returns_raw = spark.read.option("header", True).csv(f"{RAW_PATH}/fact_returns.csv")
fact_targets_raw = spark.read.option("header", True).csv(f"{RAW_PATH}/fact_targets.csv")

print(f"Bronze layer loaded:")
print(f"  dim_customers : {dim_customers_raw.count()} rows")
print(f"  dim_products  : {dim_products_raw.count()} rows")
print(f"  fact_sales    : {fact_sales_raw.count()} rows")
print(f"  fact_returns  : {fact_returns_raw.count()} rows")
print(f"  fact_targets  : {fact_targets_raw.count()} rows")

# %% Silver Layer — Clean, validate, and type-cast

dim_customers_silver = (
    dim_customers_raw
    .withColumn("customer_id", F.trim(F.col("customer_id")))
    .withColumn("customer_name", F.initcap(F.trim(F.col("customer_name"))))
    .withColumn("segment", F.trim(F.col("segment")))
    .withColumn("region", F.trim(F.col("region")))
    .withColumn("country", F.trim(F.col("country")))
    .dropDuplicates(["customer_id"])
    .filter(F.col("customer_id").isNotNull())
)

dim_products_silver = (
    dim_products_raw
    .withColumn("product_id", F.trim(F.col("product_id")))
    .withColumn("product_name", F.trim(F.col("product_name")))
    .withColumn("unit_price", F.col("unit_price").cast(DoubleType()))
    .withColumn("unit_cost", F.col("unit_cost").cast(DoubleType()))
    .withColumn("profit_margin", F.round(
        (F.col("unit_price") - F.col("unit_cost")) / F.col("unit_price"), 4
    ))
    .dropDuplicates(["product_id"])
    .filter(F.col("unit_price") > 0)
)

dim_date_silver = (
    dim_date_raw
    .withColumn("date_key", F.col("date_key").cast(IntegerType()))
    .withColumn("full_date", F.to_date(F.col("full_date"), "yyyy-MM-dd"))
    .withColumn("year", F.col("year").cast(IntegerType()))
    .withColumn("month", F.col("month").cast(IntegerType()))
    .withColumn("is_weekend", F.col("is_weekend").cast(IntegerType()))
    .withColumn("year_month", F.date_format(F.col("full_date"), "yyyy-MM"))
)

fact_sales_silver = (
    fact_sales_raw
    .withColumn("order_date", F.to_date(F.col("order_date"), "yyyy-MM-dd"))
    .withColumn("ship_date", F.to_date(F.col("ship_date"), "yyyy-MM-dd"))
    .withColumn("quantity", F.col("quantity").cast(IntegerType()))
    .withColumn("unit_price", F.col("unit_price").cast(DoubleType()))
    .withColumn("discount_pct", F.col("discount_pct").cast(DoubleType()))
    .withColumn("total_amount", F.col("total_amount").cast(DoubleType()))
    .withColumn("cost_amount", F.col("cost_amount").cast(DoubleType()))
    .withColumn("profit", F.col("profit").cast(DoubleType()))
    .withColumn("shipping_days", F.datediff(F.col("ship_date"), F.col("order_date")))
    .filter(F.col("quantity") > 0)
    .filter(F.col("total_amount") > 0)
    .dropDuplicates(["order_id"])
)

fact_returns_silver = (
    fact_returns_raw
    .withColumn("return_date", F.to_date(F.col("return_date"), "yyyy-MM-dd"))
    .withColumn("quantity", F.col("quantity").cast(IntegerType()))
    .withColumn("refund_amount", F.col("refund_amount").cast(DoubleType()))
    .filter(F.col("refund_amount") > 0)
    .dropDuplicates(["return_id"])
)

fact_targets_silver = (
    fact_targets_raw
    .withColumn("year", F.col("year").cast(IntegerType()))
    .withColumn("month", F.col("month").cast(IntegerType()))
    .withColumn("target_revenue", F.col("target_revenue").cast(DoubleType()))
    .withColumn("target_orders", F.col("target_orders").cast(IntegerType()))
)

staging_tables = {
    "dim_customers": dim_customers_silver,
    "dim_products": dim_products_silver,
    "dim_date": dim_date_silver,
    "fact_sales": fact_sales_silver,
    "fact_returns": fact_returns_silver,
    "fact_targets": fact_targets_silver,
}

for name, df in staging_tables.items():
    df.write.mode("overwrite").parquet(f"{STAGING_PATH}/{name}")
    print(f"Silver: {name} → {df.count()} rows written to staging")

# %% Gold Layer — Curated Delta tables with business logic

dim_customers_silver.write.mode("overwrite").format("delta").saveAsTable("SalesLakehouse.dim_customers")
dim_products_silver.write.mode("overwrite").format("delta").saveAsTable("SalesLakehouse.dim_products")
dim_date_silver.write.mode("overwrite").format("delta").saveAsTable("SalesLakehouse.dim_date")

(
    dim_sales_reps_raw
    .withColumn("rep_id", F.trim(F.col("rep_id")))
    .withColumn("rep_name", F.trim(F.col("rep_name")))
    .withColumn("region", F.trim(F.col("region")))
    .write.mode("overwrite").format("delta").saveAsTable("SalesLakehouse.dim_sales_reps")
)

fact_sales_silver.write.mode("overwrite").format("delta").saveAsTable("SalesLakehouse.fact_sales")
fact_returns_silver.write.mode("overwrite").format("delta").saveAsTable("SalesLakehouse.fact_returns")
fact_targets_silver.write.mode("overwrite").format("delta").saveAsTable("SalesLakehouse.fact_targets")

print("Gold layer: All Delta tables written to Lakehouse")

# %% Gold Layer — Aggregated views

monthly_summary = (
    fact_sales_silver
    .join(dim_customers_silver, "customer_id")
    .join(dim_products_silver, "product_id")
    .withColumn("year", F.year("order_date"))
    .withColumn("month", F.month("order_date"))
    .groupBy("year", "month", "region", "category")
    .agg(
        F.countDistinct("order_id").alias("total_orders"),
        F.countDistinct("customer_id").alias("unique_customers"),
        F.sum("quantity").alias("total_quantity"),
        F.round(F.sum("total_amount"), 2).alias("total_revenue"),
        F.round(F.sum("cost_amount"), 2).alias("total_cost"),
        F.round(F.sum("profit"), 2).alias("total_profit"),
        F.round(F.avg("discount_pct"), 4).alias("avg_discount"),
    )
)
monthly_summary.write.mode("overwrite").format("delta").saveAsTable("SalesLakehouse.gold_monthly_summary")

# RFM segmentation
from pyspark.sql.window import Window

rfm_base = (
    fact_sales_silver
    .join(dim_customers_silver, "customer_id")
    .groupBy("customer_id", "customer_name", "segment", "region")
    .agg(
        F.datediff(F.lit("2025-06-30"), F.max("order_date")).alias("recency_days"),
        F.countDistinct("order_id").alias("frequency"),
        F.round(F.sum("total_amount"), 2).alias("monetary"),
    )
)

for col_name, order in [("recency_days", "desc"), ("frequency", "asc"), ("monetary", "asc")]:
    score_col = col_name[0] + "_score"
    w = Window.orderBy(F.col(col_name).desc() if order == "desc" else F.col(col_name).asc())
    rfm_base = rfm_base.withColumn(score_col, F.ntile(5).over(w))

rfm_segmented = rfm_base.withColumn(
    "customer_segment",
    F.when((F.col("r_score") >= 4) & (F.col("f_score") >= 4) & (F.col("m_score") >= 4), "Champions")
    .when((F.col("r_score") >= 3) & (F.col("f_score") >= 3), "Loyal Customers")
    .when((F.col("r_score") >= 4) & (F.col("f_score") <= 2), "New Customers")
    .when((F.col("r_score") <= 2) & (F.col("f_score") >= 3), "At Risk")
    .when((F.col("r_score") <= 2) & (F.col("f_score") <= 2), "Lost")
    .otherwise("Potential Loyalists")
)
rfm_segmented.write.mode("overwrite").format("delta").saveAsTable("SalesLakehouse.gold_customer_rfm")

print("Gold layer: Aggregated and RFM tables created")

# %% Data quality summary

for table_name in ["dim_customers", "dim_products", "dim_date", "dim_sales_reps",
                    "fact_sales", "fact_returns", "fact_targets",
                    "gold_monthly_summary", "gold_customer_rfm"]:
    df = spark.table(f"SalesLakehouse.{table_name}")
    print(f"  {table_name:30s} → {df.count():>8,} rows, {len(df.columns):>3} columns")
