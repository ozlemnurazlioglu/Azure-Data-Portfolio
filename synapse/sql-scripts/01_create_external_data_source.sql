-- ============================================================
-- STEP 1: Create External Data Source & File Format
-- Azure Synapse Analytics - Serverless SQL Pool
-- ============================================================

-- Create a master key (required for credential-based access)
CREATE MASTER KEY ENCRYPTION BY PASSWORD = '<StrongPassword>';

-- Create credential for Azure Data Lake Storage Gen2
CREATE DATABASE SCOPED CREDENTIAL SalesDataLakeCredential
WITH IDENTITY = 'SHARED ACCESS SIGNATURE',
SECRET = '<your-sas-token>';

-- Create external data source pointing to ADLS Gen2
CREATE EXTERNAL DATA SOURCE SalesDataLake
WITH (
    LOCATION = 'https://<storage-account>.dfs.core.windows.net/sales-data',
    CREDENTIAL = SalesDataLakeCredential
);

-- Create external file format for CSV files
CREATE EXTERNAL FILE FORMAT CsvFormat
WITH (
    FORMAT_TYPE = DELIMITEDTEXT,
    FORMAT_OPTIONS (
        FIELD_TERMINATOR = ',',
        STRING_DELIMITER = '"',
        FIRST_ROW = 2,
        USE_TYPE_DEFAULT = TRUE,
        ENCODING = 'UTF8'
    )
);

-- Create external file format for Parquet files (optimized)
CREATE EXTERNAL FILE FORMAT ParquetFormat
WITH (
    FORMAT_TYPE = PARQUET,
    DATA_COMPRESSION = 'org.apache.hadoop.io.compress.SnappyCodec'
);
