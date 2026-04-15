// Power Query (M) — dim_customers transformation
// Source: CSV file or Azure Data Lake Gen2

let
    Source = Csv.Document(
        File.Contents("dim_customers.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.None]
    ),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),

    #"Changed Types" = Table.TransformColumnTypes(#"Promoted Headers", {
        {"customer_id", type text},
        {"customer_name", type text},
        {"segment", type text},
        {"region", type text},
        {"country", type text}
    }),

    #"Trimmed Text" = Table.TransformColumns(#"Changed Types", {
        {"customer_name", Text.Trim, type text},
        {"region", Text.Trim, type text},
        {"country", Text.Trim, type text}
    }),

    #"Proper Case Names" = Table.TransformColumns(#"Trimmed Text", {
        {"customer_name", Text.Proper, type text}
    }),

    #"Removed Duplicates" = Table.Distinct(#"Proper Case Names", {"customer_id"}),

    #"Filtered Blanks" = Table.SelectRows(#"Removed Duplicates", each
        [customer_id] <> null and [customer_id] <> ""
    ),

    #"Added Region Sort" = Table.AddColumn(#"Filtered Blanks", "RegionSort", each
        if [region] = "North America" then 1
        else if [region] = "Europe" then 2
        else if [region] = "Asia Pacific" then 3
        else if [region] = "Latin America" then 4
        else if [region] = "Middle East & Africa" then 5
        else 6,
        Int64.Type
    ),

    #"Renamed Columns" = Table.RenameColumns(#"Added Region Sort", {
        {"customer_id", "Customer ID"},
        {"customer_name", "Customer Name"},
        {"segment", "Segment"},
        {"region", "Region"},
        {"country", "Country"}
    })
in
    #"Renamed Columns"
