# Azure Data & Power Platform Portfolio

End-to-end enterprise data analytics solution demonstrating Azure Data Engineering, Microsoft Fabric, Power BI reporting, and Microsoft Power Platform automation.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                                     │
│  CSV Files  │  APIs  │  SharePoint Lists  │  SQL Databases  │  Excel   │
└──────┬──────────┬──────────┬────────────────┬──────────────────┬────────┘
       │          │          │                │                  │
       ▼          ▼          ▼                ▼                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    AZURE DATA LAKE GEN2 / ONELAKE                       │
│           raw/            staging/            curated/                   │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ AZURE SYNAPSE    │ │ MICROSOFT FABRIC │ │ AD-HOC ANALYSIS  │
│                  │ │                  │ │                  │
│ • Pipelines      │ │ • Lakehouse      │ │ • Python/pandas  │
│ • Serverless SQL │ │ • Spark Notebooks│ │ • scipy/sklearn  │
│ • Spark Pool     │ │ • Dataflow Gen2  │ │ • statsmodels    │
│ • OPENROWSET     │ │ • Direct Lake    │ │ • Visualization  │
└────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘
         │                    │                     │
         └────────────────────┼─────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       POWER BI                                          │
│                                                                         │
│  ┌─────────────────┐  ┌──────────────┐  ┌────────────────────────────┐│
│  │ Tabular Model   │  │ DAX Measures │  │ Reports & Dashboards       ││
│  │ (Star Schema)   │  │ (50+ KPIs)   │  │ (6 Interactive Pages)      ││
│  └─────────────────┘  └──────────────┘  └────────────────────────────┘│
│  ┌─────────────────┐  ┌──────────────┐  ┌────────────────────────────┐│
│  │ Power Query (M) │  │ RLS/OLS      │  │ Gateway & Scheduled        ││
│  │ Transformations  │  │ Security     │  │ Refresh                    ││
│  └─────────────────┘  └──────────────┘  └────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  POWER PLATFORM                                         │
│                                                                         │
│  ┌──────────────────────┐    ┌──────────────────────────────────────┐  │
│  │ Power Automate        │    │ Power Apps                          │  │
│  │ • Weekly Report Flow  │    │ • Inventory Management CRUD App    │  │
│  │ • Approval Workflow   │    │ • SharePoint/Dataverse Backend     │  │
│  │ • Pipeline Monitor    │    │ • Responsive Canvas App            │  │
│  └──────────────────────┘    └──────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
azure-data-portfolio/
│
├── data/                           # Sample datasets
│   ├── generate_data.py            # Python script to generate realistic data
│   ├── dim_products.csv            # 75 products across 5 categories
│   ├── dim_customers.csv           # 200 customers across 5 regions
│   ├── dim_sales_reps.csv          # 10 sales representatives
│   ├── dim_date.csv                # Date dimension (2023-2025)
│   ├── fact_sales.csv              # 12,700+ sales transactions
│   ├── fact_returns.csv            # 800 return records
│   └── fact_targets.csv            # Monthly revenue targets
│
├── synapse/                        # Azure Synapse Analytics
│   ├── README.md                   # Pipeline architecture documentation
│   ├── sql-scripts/
│   │   ├── 01_create_external_data_source.sql
│   │   ├── 02_create_external_tables.sql
│   │   ├── 03_create_views.sql     # Denormalized, monthly, RFM views
│   │   └── 04_openrowset_queries.sql
│   └── pipeline-definitions/
│       └── sales_etl_pipeline.json # Full ETL pipeline definition
│
├── fabric/                         # Microsoft Fabric
│   ├── README.md                   # Fabric architecture & deployment guide
│   ├── notebooks/
│   │   └── sales_transform_notebook.py  # PySpark medallion ETL (Bronze→Silver→Gold)
│   ├── lakehouse/
│   │   └── lakehouse_config.json   # Lakehouse table & schedule config
│   └── dataflow-gen2/
│       └── sales_dataflow.json     # No-code Power Query Online transformation
│
├── power-bi/                       # Power BI solution
│   ├── README.md                   # Power BI documentation
│   ├── Sales Analytics.pbix        # Power BI report file
│   ├── dax-measures/
│   │   └── sales_measures.dax      # 50+ DAX measures with time intelligence
│   ├── data-model/
│   │   ├── data_model.md           # Star schema documentation & relationships
│   │   └── rls_setup.dax           # RLS/OLS security configuration
│   └── power-query/
│       ├── dim_customers.pq        # Customer dimension M transform
│       ├── dim_products.pq         # Product dimension with profit margin & price tier
│       ├── dim_date.pq             # Date table with fiscal calendar & sort columns
│       ├── fact_sales.pq           # Sales fact with shipping days & discount tiers
│       └── fact_returns.pq         # Returns with category classification
│
├── power-automate/                 # Power Automate flows
│   ├── README.md                   # 3 flow designs with diagrams
│   └── flow_definitions/
│       ├── sales_report_flow.json  # Weekly report generator flow
│       ├── approval_workflow.json  # Multi-level PO approval flow
│       └── pipeline_monitor_flow.json  # Synapse pipeline failure alerting
│
├── power-apps/                     # Power Apps solution
│   ├── README.md                   # Inventory CRUD app with formulas
│   └── app-definition/
│       └── inventory_app.json      # App screens, controls & data source definition
│
├── analysis/                       # Ad-hoc Data Analysis
│   ├── README.md                   # Analysis methodology & findings
│   ├── sales_analysis.py           # Statistical analysis & ML segmentation
│   └── outputs/                    # Generated charts (correlation, clustering, etc.)
│
└── docs/                           # Additional documentation
    ├── architecture/
    │   └── architecture_overview.md # Detailed architecture with diagrams
    └── screenshots/                # Dashboard screenshots
        ├── 01_executive_summary.png
        └── 02_sales_performance.png
```

## Technologies & Skills Demonstrated

| Area | Technologies |
|------|-------------|
| **Data Engineering** | Azure Synapse Analytics, Data Lake Gen2, Serverless SQL, Spark |
| **Microsoft Fabric** | Lakehouse, Spark Notebooks, Dataflow Gen2, OneLake, Delta Lake, Direct Lake |
| **ETL/ELT** | Synapse Pipelines, Copy Activity, Medallion Architecture (Bronze/Silver/Gold) |
| **Data Modeling** | Star Schema, Tabular Model, Dimension/Fact tables |
| **Analytics & BI** | Power BI, DAX (50+ measures), Power Query M, Time Intelligence |
| **Security** | Row-Level Security (RLS), Object-Level Security (OLS), Managed Identity |
| **Automation** | Power Automate: Approval Workflows, Scheduled Flows, API Integration |
| **App Development** | Power Apps Canvas App, CRUD operations, SharePoint/Dataverse backend |
| **Data Sources** | MSSQL (Serverless), SharePoint, CSV, Parquet, REST API, Excel |
| **Cloud** | Azure (Synapse, ADLS Gen2, Azure AD, Managed Identity), Microsoft Fabric |
| **Data Analysis** | Python (pandas, scipy, scikit-learn, statsmodels), Statistical Testing, K-Means |

## Dashboard Screenshots

### Executive Summary
![Executive Summary](docs/screenshots/01_executive_summary.png)

### Sales Performance
![Sales Performance](docs/screenshots/02_sales_performance.png)

## Key Highlights

- **12,700+ realistic sales transactions** across 5 global regions
- **Star Schema** data model with 3 fact tables and 4 dimension tables
- **50+ DAX measures** including YoY growth, rolling averages, RFM segmentation
- **Power Query (M)** transformations with proper formatting and business logic
- **Row-Level & Object-Level Security** for enterprise data governance
- **Microsoft Fabric** implementation with Lakehouse, Spark Notebooks, and Dataflow Gen2
- **Serverless SQL** queries with OPENROWSET, External Tables, and CETAS
- **Customer RFM Analysis** (Recency, Frequency, Monetary) segmentation — SQL + Python + Spark
- **End-to-end ETL pipeline** with validation, transformation, and Power BI refresh
- **3 Power Automate flows** with full JSON definitions: report generation, purchase approval, pipeline monitoring
- **Inventory Management App** with search, filtering, stock alerts, and audit trail
- **Statistical analysis**: correlation, hypothesis testing, time-series decomposition, K-Means clustering
- **Medallion Architecture** (Bronze → Silver → Gold) in both Synapse and Fabric

## Getting Started

### Prerequisites
- Azure subscription (free tier works for Synapse Serverless SQL)
- Power BI Desktop (free)
- Microsoft 365 license (for Power Apps & Power Automate)
- Microsoft Fabric capacity (Trial or F64+ for Fabric components)
- Python 3.8+ with pandas, scipy, scikit-learn, statsmodels (for analysis scripts)

### Quick Start

1. **Clone this repository**
   ```bash
   git clone https://github.com/<your-username>/azure-data-portfolio.git
   ```

2. **Generate sample data** (or use the included CSVs)
   ```bash
   python data/generate_data.py
   ```

3. **Power BI**: Open `power-bi/Sales Analytics.pbix` or Get Data → CSV → Load files from `data/`

4. **Synapse**: Execute SQL scripts in order (01 → 04) in Synapse Studio

5. **Fabric**: Upload CSVs to Lakehouse `Files/raw/`, then run the Spark notebook

6. **Power Automate**: Import flow JSONs from `power-automate/flow_definitions/`

7. **Power Apps**: Create SharePoint lists per schema in `power-apps/README.md`, then import app definition

8. **Analysis**: Run statistical analysis
   ```bash
   pip install pandas numpy scipy scikit-learn statsmodels matplotlib seaborn
   python analysis/sales_analysis.py
   ```


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
