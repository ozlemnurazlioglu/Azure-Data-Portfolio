# Data Model Documentation

## Star Schema Design

This Power BI solution uses a **Star Schema** architecture for optimal query performance and intuitive data modeling.

```
                    ┌──────────────────┐
                    │   dim_date       │
                    │──────────────────│
                    │ date_key (PK)    │
                    │ full_date        │
                    │ year             │
                    │ quarter          │
                    │ month            │
                    │ month_name       │
                    │ day_of_week      │
                    │ is_weekend       │
                    │ fiscal_year      │
                    │ fiscal_quarter   │
                    └────────┬─────────┘
                             │
┌──────────────────┐         │         ┌──────────────────┐
│ dim_customers    │         │         │ dim_products     │
│──────────────────│    ┌────┴────┐    │──────────────────│
│ customer_id (PK) ├────┤         ├────┤ product_id (PK)  │
│ customer_name    │    │  fact_  │    │ product_name     │
│ segment          │    │  sales  │    │ category         │
│ region           │    │         │    │ sub_category     │
│ country          │    └────┬────┘    │ unit_price       │
└──────────────────┘         │         │ unit_cost        │
                             │         └──────────────────┘
                    ┌────────┴─────────┐
                    │ dim_sales_reps   │
                    │──────────────────│
                    │ rep_id (PK)      │
                    │ rep_name         │
                    │ region           │
                    └──────────────────┘

fact_sales (Fact Table)
─────────────────────────────
order_id          (PK)
order_date        → dim_date[full_date]
ship_date
customer_id       → dim_customers[customer_id]
product_id        → dim_products[product_id]
rep_id            → dim_sales_reps[rep_id]
channel
payment_method
quantity
unit_price
discount_pct
total_amount
cost_amount
profit

fact_returns (Fact Table)
─────────────────────────────
return_id         (PK)
original_order_id → fact_sales[order_id]
return_date
product_id        → dim_products[product_id]
quantity
reason
refund_amount

fact_targets (Fact Table)
─────────────────────────────
year
month
region            → dim_customers[region]
category          → dim_products[category]
target_revenue
target_orders
```

## Relationships

| From Table | From Column | To Table | To Column | Cardinality | Cross Filter |
|------------|-------------|----------|-----------|-------------|--------------|
| fact_sales | order_date | dim_date | full_date | Many-to-One | Single |
| fact_sales | customer_id | dim_customers | customer_id | Many-to-One | Single |
| fact_sales | product_id | dim_products | product_id | Many-to-One | Single |
| fact_sales | rep_id | dim_sales_reps | rep_id | Many-to-One | Single |
| fact_returns | product_id | dim_products | product_id | Many-to-One | Single |
| fact_returns | return_date | dim_date | full_date | Many-to-One | Single |

## Row-Level Security (RLS)

### Roles Defined

| Role Name | Table | DAX Filter Expression | Description |
|-----------|-------|----------------------|-------------|
| Regional Manager - NA | dim_customers | `[region] = "North America"` | Restricts to North America data |
| Regional Manager - EU | dim_customers | `[region] = "Europe"` | Restricts to Europe data |
| Regional Manager - APAC | dim_customers | `[region] = "Asia Pacific"` | Restricts to Asia Pacific data |
| Regional Manager - LATAM | dim_customers | `[region] = "Latin America"` | Restricts to Latin America data |
| Regional Manager - MEA | dim_customers | `[region] = "Middle East & Africa"` | Restricts to MEA data |
| Sales Rep | dim_sales_reps | `[rep_name] = USERPRINCIPALNAME()` | Dynamic RLS based on logged-in user |

### RLS Implementation Steps

1. In Power BI Desktop → Modeling → Manage Roles
2. Create each role with the filter expression above
3. Test via "View As Roles" in the Modeling tab
4. After publishing to Power BI Service, assign users to roles in Dataset Security settings

### Object-Level Security (OLS)

| Role | Restricted Columns | Reason |
|------|-------------------|--------|
| Sales Rep | `fact_sales[cost_amount]`, `dim_products[unit_cost]` | Cost data restricted to managers |
| Sales Rep | `fact_sales[profit]` | Profit visibility limited to leadership |

## Power Query (M) Transformations

Key transformations applied during data load:

```m
// Date table marked as Date table for time intelligence
let
    Source = Csv.Document(File.Contents("dim_date.csv")),
    #"Promoted Headers" = Table.PromoteHeaders(Source),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers", {
        {"date_key", Int64.Type},
        {"full_date", type date},
        {"year", Int64.Type},
        {"quarter", type text},
        {"month", Int64.Type},
        {"month_name", type text},
        {"day_of_week", type text},
        {"is_weekend", Int64.Type},
        {"fiscal_year", type text},
        {"fiscal_quarter", type text}
    }),
    #"Sort Order" = Table.AddColumn(#"Changed Type", "MonthSort", each [month]),
    #"Day Sort" = Table.AddColumn(#"Sort Order", "DaySort", each 
        if [day_of_week] = "Monday" then 1
        else if [day_of_week] = "Tuesday" then 2
        else if [day_of_week] = "Wednesday" then 3
        else if [day_of_week] = "Thursday" then 4
        else if [day_of_week] = "Friday" then 5
        else if [day_of_week] = "Saturday" then 6
        else 7
    )
in
    #"Day Sort"
```

## Dashboard Pages

| Page | Purpose | Key Visuals |
|------|---------|-------------|
| Executive Summary | High-level KPIs and trends | KPI cards, Revenue trend line, Top 5 categories bar chart |
| Sales Performance | Detailed sales analysis | Matrix by region/product, Waterfall chart, Scatter plot |
| Customer Analytics | Customer segmentation & behavior | Donut chart by segment, Customer growth trend, CLV distribution |
| Product Deep Dive | Product-level performance | Treemap, Product rank table, Return rate analysis |
| Regional Analysis | Geographic performance | Map visual, Region comparison bar chart, Target vs Actual |
| Drill-Through Detail | Order-level details | Detailed table with all order attributes |

## Bookmarks & Navigation

- **Dark/Light Theme Toggle**: Bookmark-based theme switching
- **Reset Filters**: Clears all slicers to default state
- **Export View**: Optimized layout for PDF export
- **Drill-Through**: Right-click on any product/customer to see detailed order history
