# Ad-hoc Data Analysis & Statistical Modeling

## Overview

Python-based analytical scripts for exploratory data analysis, statistical testing, and machine learning segmentation on the Sales Analytics dataset.

## Analyses Performed

| # | Analysis | Method | Key Insight |
|---|----------|--------|-------------|
| 1 | **Correlation Analysis** | Pearson & Spearman correlation | Identifies relationships between price, quantity, discount, and profit |
| 2 | **Hypothesis Testing** | Welch's t-test | Tests Online vs Retail AOV difference and discount impact on margins |
| 3 | **Time-Series Decomposition** | Additive decomposition (statsmodels) | Separates trend, 30-day seasonality, and residual noise from daily revenue |
| 4 | **Customer Segmentation** | K-Means clustering on RFM | Segments 200 customers into Champions, Loyal, At Risk, Lost |
| 5 | **Regional × Category Analysis** | Chi-square independence test | Determines if region influences product category mix |
| 6 | **Discount Effectiveness** | Tier-based aggregation | Measures profitability and volume impact across discount tiers |

## Output Charts

Generated in `outputs/` directory:

- `correlation_matrix.png` — Pearson & Spearman heatmaps
- `timeseries_decomposition.png` — Trend/seasonal/residual breakdown
- `customer_segmentation.png` — Elbow method, scatter plot, segment comparison
- `regional_category_analysis.png` — Stacked bar + monthly trend by region
- `discount_analysis.png` — Profit and volume by discount tier

## Requirements

```bash
pip install pandas numpy scipy scikit-learn statsmodels matplotlib seaborn
```

## Usage

```bash
cd analysis
python sales_analysis.py
```

## Key Findings

- **Quantity × Revenue**: Strong positive correlation (r > 0.85)
- **Discount × Profit**: Negative correlation — higher discounts erode margins
- **Seasonality**: Clear November–December revenue spike (holiday season)
- **Customer Segments**: ~20% of customers classified as "Champions" driving ~50% of revenue
- **Region Independence**: Region significantly influences category purchasing patterns (p < 0.05)
