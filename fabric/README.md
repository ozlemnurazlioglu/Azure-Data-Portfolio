# Microsoft Fabric - Lakehouse Analytics

## Overview

Microsoft Fabric implementation for the Sales Analytics solution, demonstrating the modern data lakehouse architecture with Spark notebooks, Dataflow Gen2, and OneLake integration.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      MICROSOFT FABRIC WORKSPACE                         │
│                                                                         │
│  ┌───────────────────┐    ┌───────────────────┐    ┌─────────────────┐ │
│  │  Data Factory      │    │  Lakehouse        │    │  SQL Analytics  │ │
│  │  (Dataflow Gen2)   │───►│  (OneLake)        │───►│  Endpoint       │ │
│  │                    │    │                    │    │                 │ │
│  │  • CSV Ingestion   │    │  Tables/           │    │  • Auto-schema │ │
│  │  • Transformations │    │   ├─ dim_customers │    │  • T-SQL views │ │
│  │  • Type Casting    │    │   ├─ dim_products  │    │  • DirectQuery │ │
│  └───────────────────┘    │   ├─ dim_date      │    └─────────────────┘ │
│                            │   ├─ fact_sales    │                        │
│  ┌───────────────────┐    │   ├─ fact_returns  │    ┌─────────────────┐ │
│  │  Spark Notebooks   │    │   └─ fact_targets  │    │  Power BI       │ │
│  │                    │───►│                    │───►│  (Direct Lake)  │ │
│  │  • Cleansing       │    │  Files/             │    │                 │ │
│  │  • Enrichment      │    │   ├─ raw/          │    │  • Semantic     │ │
│  │  • Aggregation     │    │   ├─ staging/      │    │    Model        │ │
│  │  • Delta Tables    │    │   └─ curated/      │    │  • Reports      │ │
│  └───────────────────┘    └───────────────────┘    └─────────────────┘ │
│                                                                         │
│  ┌───────────────────┐    ┌───────────────────┐                        │
│  │  Data Pipelines    │    │  Data Activator   │                        │
│  │                    │    │                    │                        │
│  │  • Orchestration   │    │  • Alert on KPI   │                        │
│  │  • Scheduling      │    │    threshold       │                        │
│  │  • Error handling  │    │  • Trigger Power   │                        │
│  └───────────────────┘    │    Automate flow    │                        │
│                            └───────────────────┘                        │
└─────────────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Lakehouse (`lakehouse/`)

Delta Lake-based storage with medallion architecture:

| Layer | Format | Contents |
|-------|--------|----------|
| **Files/raw/** | CSV/Parquet | Raw ingested data from sources |
| **Files/staging/** | Parquet | Cleaned and validated data |
| **Tables/** | Delta | Curated dimension and fact tables |

### 2. Spark Notebooks (`notebooks/`)

| Notebook | Purpose |
|----------|---------|
| `sales_transform_notebook.py` | Full medallion ETL: raw → staging → curated Delta tables |

### 3. Dataflow Gen2 (`dataflow-gen2/`)

| Dataflow | Purpose |
|----------|---------|
| `sales_dataflow.json` | No-code data transformation with Power Query Online |

## Lakehouse Configuration

```json
{
  "workspace": "SalesAnalytics_WS",
  "lakehouse": "SalesLakehouse",
  "default_storage": "OneLake",
  "tables_format": "Delta",
  "sql_endpoint": "auto-generated"
}
```

## Direct Lake Mode

Power BI connects to the Lakehouse via **Direct Lake** mode:

- No data import or DirectQuery needed
- Reads Delta/Parquet files directly from OneLake
- Automatic V-Order optimization
- Sub-second query performance on large datasets

## Data Pipeline Schedule

| Pipeline | Trigger | Description |
|----------|---------|-------------|
| PL_Fabric_Daily_ETL | Daily 06:00 UTC | Full medallion refresh |
| PL_Fabric_Incremental | Every 4 hours | Incremental load for fact_sales |
| DA_Revenue_Alert | Real-time | Data Activator alert on revenue drop >15% |

## Deployment

1. Create a Fabric workspace with Trial or F64+ capacity
2. Create a Lakehouse named `SalesLakehouse`
3. Upload CSV files to `Files/raw/`
4. Import and run the Spark notebook
5. Create Dataflow Gen2 from the JSON definition
6. Connect Power BI via Direct Lake to the Lakehouse SQL endpoint
