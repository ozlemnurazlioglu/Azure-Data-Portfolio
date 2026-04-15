"""
Sales Data — Ad-hoc Statistical Analysis & Modeling
====================================================
Demonstrates: correlation analysis, hypothesis testing, time-series
decomposition, customer clustering (K-Means), and sales forecasting.

Requirements:
    pip install pandas numpy scipy scikit-learn statsmodels matplotlib seaborn
"""

import os
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.seasonal import seasonal_decompose

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid", palette="muted")

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_data():
    """Load all CSV data and merge into analytical dataframes."""
    sales = pd.read_csv(os.path.join(DATA_DIR, "fact_sales.csv"), parse_dates=["order_date", "ship_date"])
    returns = pd.read_csv(os.path.join(DATA_DIR, "fact_returns.csv"), parse_dates=["return_date"])
    targets = pd.read_csv(os.path.join(DATA_DIR, "fact_targets.csv"))
    customers = pd.read_csv(os.path.join(DATA_DIR, "dim_customers.csv"))
    products = pd.read_csv(os.path.join(DATA_DIR, "dim_products.csv"))
    dates = pd.read_csv(os.path.join(DATA_DIR, "dim_date.csv"), parse_dates=["full_date"])

    sales_enriched = (
        sales
        .merge(customers, on="customer_id", how="left")
        .merge(products, on="product_id", how="left", suffixes=("", "_prod"))
    )
    return sales_enriched, returns, targets, customers, products, dates


# ── 1. Correlation Analysis ─────────────────────────────────────────────────

def correlation_analysis(sales: pd.DataFrame):
    """Pearson & Spearman correlation between numeric sales features."""
    numeric_cols = ["quantity", "unit_price", "discount_pct", "total_amount", "cost_amount", "profit"]
    corr_pearson = sales[numeric_cols].corr(method="pearson")
    corr_spearman = sales[numeric_cols].corr(method="spearman")

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    sns.heatmap(corr_pearson, annot=True, fmt=".2f", cmap="RdYlGn", ax=axes[0], vmin=-1, vmax=1)
    axes[0].set_title("Pearson Correlation")
    sns.heatmap(corr_spearman, annot=True, fmt=".2f", cmap="RdYlGn", ax=axes[1], vmin=-1, vmax=1)
    axes[1].set_title("Spearman Correlation")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "correlation_matrix.png"), dpi=150)
    plt.close()

    print("═══ Correlation Analysis ═══")
    print(f"Discount ↔ Profit (Pearson):  r = {corr_pearson.loc['discount_pct', 'profit']:.3f}")
    print(f"Quantity ↔ Revenue (Pearson): r = {corr_pearson.loc['quantity', 'total_amount']:.3f}")
    return corr_pearson


# ── 2. Hypothesis Testing ───────────────────────────────────────────────────

def hypothesis_tests(sales: pd.DataFrame):
    """
    H1: Online channel generates higher average order value than Retail Store.
    H2: Discounted orders have different profit margins than non-discounted.
    """
    online = sales[sales["channel"] == "Online"]["total_amount"]
    retail = sales[sales["channel"] == "Retail Store"]["total_amount"]

    t_stat, p_value = stats.ttest_ind(online, retail, equal_var=False)
    print("\n═══ Hypothesis Test 1: Online vs Retail AOV ═══")
    print(f"Online AOV:  ${online.mean():,.2f}   (n={len(online):,})")
    print(f"Retail AOV:  ${retail.mean():,.2f}   (n={len(retail):,})")
    print(f"t-statistic: {t_stat:.4f},  p-value: {p_value:.6f}")
    print(f"Result: {'Reject H0 — significant difference' if p_value < 0.05 else 'Fail to reject H0'}")

    discounted = sales[sales["discount_pct"] > 0]["profit"] / sales[sales["discount_pct"] > 0]["total_amount"]
    full_price = sales[sales["discount_pct"] == 0]["profit"] / sales[sales["discount_pct"] == 0]["total_amount"]

    t2, p2 = stats.ttest_ind(discounted.dropna(), full_price.dropna(), equal_var=False)
    print("\n═══ Hypothesis Test 2: Discount Impact on Margin ═══")
    print(f"Discounted margin:  {discounted.mean():.4f}")
    print(f"Full-price margin:  {full_price.mean():.4f}")
    print(f"t-statistic: {t2:.4f},  p-value: {p2:.6f}")
    print(f"Result: {'Reject H0 — discounts affect margin' if p2 < 0.05 else 'Fail to reject H0'}")

    return {"online_vs_retail": (t_stat, p_value), "discount_margin": (t2, p2)}


# ── 3. Time-Series Decomposition ────────────────────────────────────────────

def time_series_analysis(sales: pd.DataFrame):
    """Decompose daily revenue into trend, seasonal, and residual components."""
    daily_rev = sales.groupby("order_date")["total_amount"].sum().sort_index()
    daily_rev = daily_rev.asfreq("D", fill_value=0)

    decomposition = seasonal_decompose(daily_rev, model="additive", period=30)

    fig, axes = plt.subplots(4, 1, figsize=(16, 10), sharex=True)
    decomposition.observed.plot(ax=axes[0], title="Observed (Daily Revenue)")
    decomposition.trend.plot(ax=axes[1], title="Trend")
    decomposition.seasonal.plot(ax=axes[2], title="Seasonal (30-day cycle)")
    decomposition.resid.plot(ax=axes[3], title="Residual")
    for ax in axes:
        ax.set_xlabel("")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "timeseries_decomposition.png"), dpi=150)
    plt.close()

    print("\n═══ Time-Series Decomposition ═══")
    print(f"Period: {daily_rev.index.min()} → {daily_rev.index.max()}")
    print(f"Mean daily revenue: ${daily_rev.mean():,.2f}")
    print(f"Std daily revenue:  ${daily_rev.std():,.2f}")
    return decomposition


# ── 4. Customer Segmentation (K-Means Clustering on RFM) ────────────────────

def customer_segmentation(sales: pd.DataFrame):
    """K-Means clustering on RFM features to segment customers."""
    reference_date = sales["order_date"].max() + pd.Timedelta(days=1)

    rfm = (
        sales
        .groupby("customer_id")
        .agg(
            recency=("order_date", lambda x: (reference_date - x.max()).days),
            frequency=("order_id", "nunique"),
            monetary=("total_amount", "sum"),
        )
    )

    scaler = StandardScaler()
    rfm_scaled = scaler.fit_transform(rfm)

    inertia = []
    K_range = range(2, 9)
    for k in K_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        km.fit(rfm_scaled)
        inertia.append(km.inertia_)

    optimal_k = 4
    km_final = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
    rfm["cluster"] = km_final.fit_predict(rfm_scaled)

    segment_labels = {0: "Champions", 1: "Loyal", 2: "At Risk", 3: "Lost"}
    cluster_summary = rfm.groupby("cluster").agg(
        count=("recency", "size"),
        avg_recency=("recency", "mean"),
        avg_frequency=("frequency", "mean"),
        avg_monetary=("monetary", "mean"),
    ).sort_values("avg_monetary", ascending=False)
    cluster_summary.index = [segment_labels.get(i, f"Cluster {i}") for i in cluster_summary.index]

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    axes[0].plot(K_range, inertia, "bo-")
    axes[0].set_xlabel("Number of Clusters (k)")
    axes[0].set_ylabel("Inertia")
    axes[0].set_title("Elbow Method")
    axes[0].axvline(x=optimal_k, color="red", linestyle="--", alpha=0.7)

    scatter = axes[1].scatter(rfm["frequency"], rfm["monetary"], c=rfm["cluster"],
                               cmap="viridis", alpha=0.6, s=40)
    axes[1].set_xlabel("Frequency (orders)")
    axes[1].set_ylabel("Monetary ($)")
    axes[1].set_title("Customer Segments")
    plt.colorbar(scatter, ax=axes[1], label="Cluster")

    cluster_summary["avg_monetary"].plot(kind="barh", ax=axes[2], color=sns.color_palette("viridis", optimal_k))
    axes[2].set_xlabel("Avg Monetary ($)")
    axes[2].set_title("Segment Avg Revenue")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "customer_segmentation.png"), dpi=150)
    plt.close()

    print("\n═══ Customer Segmentation (K-Means, k=4) ═══")
    print(cluster_summary.to_string())
    return rfm, cluster_summary


# ── 5. Regional & Category Deep Dive ────────────────────────────────────────

def regional_category_analysis(sales: pd.DataFrame):
    """Cross-tabulation and chi-square test for region × category independence."""
    crosstab = pd.crosstab(sales["region"], sales["category"], values=sales["total_amount"], aggfunc="sum")
    chi2, p_val, dof, expected = stats.chi2_contingency(
        pd.crosstab(sales["region"], sales["category"])
    )

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    crosstab.plot(kind="bar", stacked=True, ax=axes[0], colormap="Set2")
    axes[0].set_title("Revenue by Region × Category")
    axes[0].set_ylabel("Revenue ($)")
    axes[0].tick_params(axis="x", rotation=30)

    region_monthly = sales.groupby([sales["order_date"].dt.to_period("M"), "region"])["total_amount"].sum().unstack()
    region_monthly.index = region_monthly.index.to_timestamp()
    region_monthly.plot(ax=axes[1], linewidth=1.5)
    axes[1].set_title("Monthly Revenue Trend by Region")
    axes[1].set_ylabel("Revenue ($)")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "regional_category_analysis.png"), dpi=150)
    plt.close()

    print("\n═══ Regional × Category Independence Test ═══")
    print(f"Chi-square: {chi2:.2f},  p-value: {p_val:.6f},  DoF: {dof}")
    print(f"Result: {'Dependent — region influences category mix' if p_val < 0.05 else 'Independent'}")
    return crosstab


# ── 6. Discount Effectiveness Analysis ───────────────────────────────────────

def discount_analysis(sales: pd.DataFrame):
    """Analyze how discount tiers affect order volume and profitability."""
    sales = sales.copy()
    sales["discount_tier"] = pd.cut(
        sales["discount_pct"],
        bins=[-0.01, 0, 0.05, 0.10, 0.15, 0.20, 1.0],
        labels=["No Discount", "1-5%", "6-10%", "11-15%", "16-20%", "20%+"]
    )

    tier_summary = sales.groupby("discount_tier", observed=True).agg(
        order_count=("order_id", "count"),
        avg_revenue=("total_amount", "mean"),
        avg_profit=("profit", "mean"),
        total_revenue=("total_amount", "sum"),
    ).round(2)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    tier_summary["avg_profit"].plot(kind="bar", ax=axes[0], color=sns.color_palette("RdYlGn_r", len(tier_summary)))
    axes[0].set_title("Avg Profit by Discount Tier")
    axes[0].set_ylabel("Avg Profit ($)")
    axes[0].tick_params(axis="x", rotation=30)

    tier_summary["order_count"].plot(kind="bar", ax=axes[1], color=sns.color_palette("Blues_d", len(tier_summary)))
    axes[1].set_title("Order Volume by Discount Tier")
    axes[1].set_ylabel("Number of Orders")
    axes[1].tick_params(axis="x", rotation=30)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "discount_analysis.png"), dpi=150)
    plt.close()

    print("\n═══ Discount Effectiveness ═══")
    print(tier_summary.to_string())
    return tier_summary


# ── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Loading data...")
    sales, returns, targets, customers, products, dates = load_data()
    print(f"Loaded {len(sales):,} sales records\n")

    corr = correlation_analysis(sales)
    hyp = hypothesis_tests(sales)
    decomp = time_series_analysis(sales)
    rfm, segments = customer_segmentation(sales)
    crosstab = regional_category_analysis(sales)
    discounts = discount_analysis(sales)

    print("\n" + "=" * 60)
    print("Analysis complete. Charts saved to analysis/outputs/")
    print("=" * 60)
