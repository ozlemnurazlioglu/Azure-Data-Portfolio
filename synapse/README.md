# Azure Synapse Analytics - Sales Data Pipeline

## Architecture

```
┌─────────────┐     ┌──────────────────────────────────────────┐     ┌───────────┐
│  Source      │     │        Azure Synapse Analytics            │     │  Power BI │
│  Systems     │     │                                          │     │  Service  │
│             │     │  ┌─────────┐  ┌──────────┐  ┌─────────┐ │     │           │
│ CSV/API/DB  ├────►│  │  Copy   ├─►│  Spark   ├─►│Serverless│─┼────►│ Dashboard │
│             │     │  │ Activity│  │ Notebook │  │ SQL Pool │ │     │           │
└─────────────┘     │  └─────────┘  └──────────┘  └─────────┘ │     └───────────┘
                    │                                          │
                    │  ┌──────────────────────────────────┐    │
                    │  │     Azure Data Lake Gen2          │    │
                    │  │  raw/ → staging/ → curated/       │    │
                    │  └──────────────────────────────────┘    │
                    └──────────────────────────────────────────┘
```

## Data Lake Zones

| Zone | Path | Format | Description |
|------|------|--------|-------------|
| **Raw** | `/raw/` | CSV | Original source data, unchanged |
| **Staging** | `/staging/` | Parquet | Validated and type-casted data |
| **Curated** | `/curated/` | Parquet (partitioned) | Enriched, denormalized, analytics-ready |

## SQL Scripts

| Script | Description |
|--------|-------------|
| `01_create_external_data_source.sql` | Setup ADLS Gen2 connection, credentials, file formats |
| `02_create_external_tables.sql` | External tables over raw CSV files |
| `03_create_views.sql` | Analytical views: denormalized, monthly summary, RFM segmentation |
| `04_openrowset_queries.sql` | Ad-hoc queries, OPENROWSET patterns, CETAS materialization |

## Pipeline

The ETL pipeline (`PL_Sales_ETL_Daily`) runs daily at 06:00 UTC:

1. **Copy Activity** - Ingest raw CSV from source to Data Lake `/raw/`
2. **Validation** - Run data quality checks (null checks, schema validation)
3. **Spark Notebook** - Transform CSV → Parquet with enrichment (joins, calculations)
4. **Serverless SQL** - Refresh curated views for Power BI consumption
5. **Power BI Refresh** - Trigger dataset refresh via REST API
6. **Notification** - Send Teams message on success/failure

## Key Features Demonstrated

- **Serverless SQL Pool**: Cost-efficient querying without provisioned resources
- **OPENROWSET**: Ad-hoc data exploration without table creation
- **CETAS**: Materialized query results as Parquet for performance
- **External Tables**: Schema-on-read over Data Lake files
- **Partitioned Data**: Year/month partitioning for query pruning
- **Data Quality**: Validation step before transformation
- **End-to-End Lineage**: Source → Raw → Curated → Power BI

## How to Deploy

1. Create Azure Synapse workspace with ADLS Gen2 storage
2. Upload CSV files to the `raw/` container
3. Execute SQL scripts in order (01 → 02 → 03 → 04)
4. Import pipeline JSON into Synapse Studio
5. Configure linked services and update placeholder values
6. Connect Power BI to Serverless SQL endpoint
