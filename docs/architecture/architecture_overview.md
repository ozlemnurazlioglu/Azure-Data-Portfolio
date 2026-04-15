# Architecture Overview

## End-to-End Data Flow

```
 ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
 │   SOURCE     │     │   INGEST     │     │  TRANSFORM   │     │   SERVE      │
 │   SYSTEMS    │────►│   LAYER      │────►│   LAYER      │────►│   LAYER      │
 └─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘

       CSV               Azure              Synapse             Power BI
       API               Data Lake          Spark Pool          DirectQuery
       SharePoint         Gen2 (raw)        Serverless SQL      Direct Lake
       SQL DB                               Fabric Notebooks    Semantic Model
       Excel                                Dataflow Gen2
```

## Detailed Architecture

### 1. Data Ingestion

| Source | Method | Destination |
|--------|--------|-------------|
| CSV Files | Synapse Copy Activity / Fabric Dataflow | ADLS Gen2 `raw/` / OneLake `Files/raw/` |
| REST API | HTTP connector in pipeline | ADLS Gen2 `raw/` |
| SharePoint Lists | Power Automate connector | SharePoint → Power Apps / Flow actions |
| SQL Database | Linked Service / OPENROWSET | Serverless SQL external tables |

### 2. Storage — Azure Data Lake Gen2 + OneLake

```
ADLS Gen2 / OneLake
├── raw/                    ← Untouched source data (CSV, JSON, Parquet)
│   ├── dim_customers.csv
│   ├── dim_products.csv
│   ├── dim_date.csv
│   ├── dim_sales_reps.csv
│   ├── fact_sales.csv
│   ├── fact_returns.csv
│   └── fact_targets.csv
│
├── staging/                ← Cleaned, validated (Parquet)
│   ├── dim_customers/
│   ├── dim_products/
│   └── fact_sales/
│
└── curated/                ← Business-ready (Delta Tables)
    ├── dim_customers/
    ├── dim_products/
    ├── fact_sales/
    ├── gold_monthly_summary/
    └── gold_customer_rfm/
```

### 3. Processing

| Engine | Use Case | Location |
|--------|----------|----------|
| **Synapse Pipelines** | Orchestration (Copy → Validate → Transform → Refresh) | `synapse/pipeline-definitions/` |
| **Serverless SQL Pool** | External tables, analytical views, OPENROWSET ad-hoc | `synapse/sql-scripts/` |
| **Fabric Spark Notebook** | PySpark medallion ETL (Bronze → Silver → Gold) | `fabric/notebooks/` |
| **Fabric Dataflow Gen2** | No-code Power Query Online transformation | `fabric/dataflow-gen2/` |

### 4. Semantic Layer — Power BI

```
┌─────────────────────────────────────────────────┐
│              POWER BI SEMANTIC MODEL              │
│                                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │
│  │ Star     │  │ 50+ DAX  │  │ RLS / OLS    │   │
│  │ Schema   │  │ Measures │  │ Security     │   │
│  │ (7 tbl)  │  │          │  │ (6 roles)    │   │
│  └──────────┘  └──────────┘  └──────────────┘   │
│                                                   │
│  ┌──────────────────────────────────────────┐    │
│  │ 6 Report Pages                            │    │
│  │ Executive │ Sales Perf │ Customer │ ...   │    │
│  └──────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

### 5. Automation & Apps

```
┌──────────────────────────┐     ┌──────────────────────────┐
│    POWER AUTOMATE         │     │    POWER APPS             │
│                           │     │                           │
│  Flow 1: Weekly Report    │     │  Inventory Management     │
│    SharePoint → Excel →   │     │  Canvas App               │
│    Teams + Email          │     │                           │
│                           │     │  • CRUD operations        │
│  Flow 2: PO Approval      │     │  • SharePoint backend     │
│    SP trigger → Approvals │     │  • Search & filter        │
│    → SP update → Teams    │     │  • Stock alerts           │
│                           │     │  • Dashboard KPIs         │
│  Flow 3: Pipeline Monitor  │     │  • Responsive layout     │
│    Synapse API → Parse →  │     │                           │
│    Alert on failure       │     │  Triggers Power Automate  │
└──────────────────────────┘     │  for low-stock reorders   │
                                  └──────────────────────────┘
```

### 6. Security Model

| Layer | Implementation |
|-------|---------------|
| **Data Lake** | Azure RBAC + ACL on ADLS Gen2 containers |
| **Synapse** | Managed Identity for pipeline authentication |
| **Power BI RLS** | 5 static regional roles + 1 dynamic role via `USERPRINCIPALNAME()` |
| **Power BI OLS** | Cost/profit columns hidden from Sales Rep role (Tabular Editor) |
| **Power Apps** | SharePoint list permissions + Azure AD security groups |
| **Power Automate** | Managed Identity for Synapse API; delegated permissions for M365 |

## Technology Stack

| Category | Services |
|----------|----------|
| **Compute** | Azure Synapse (Serverless SQL, Spark), Microsoft Fabric (Spark, Dataflow Gen2) |
| **Storage** | Azure Data Lake Gen2, OneLake, Delta Lake |
| **BI** | Power BI (Tabular, DAX, Power Query M, Direct Lake) |
| **Automation** | Power Automate (scheduled, triggered, approval flows) |
| **Apps** | Power Apps (Canvas App, SharePoint/Dataverse) |
| **Security** | Azure AD, Managed Identity, RLS/OLS, RBAC |
| **Analysis** | Python (pandas, scikit-learn, scipy, statsmodels) |
