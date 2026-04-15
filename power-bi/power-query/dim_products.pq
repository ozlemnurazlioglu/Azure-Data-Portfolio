// Power Query (M) — dim_products transformation
// Source: CSV file or Azure Data Lake Gen2

let
    Source = Csv.Document(
        File.Contents("dim_products.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.None]
    ),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),

    #"Changed Types" = Table.TransformColumnTypes(#"Promoted Headers", {
        {"product_id", type text},
        {"product_name", type text},
        {"category", type text},
        {"sub_category", type text},
        {"unit_price", Currency.Type},
        {"unit_cost", Currency.Type}
    }),

    #"Trimmed Names" = Table.TransformColumns(#"Changed Types", {
        {"product_name", Text.Trim, type text},
        {"category", Text.Trim, type text},
        {"sub_category", Text.Trim, type text}
    }),

    #"Added Profit Margin" = Table.AddColumn(#"Trimmed Names", "Profit Margin %", each
        if [unit_price] > 0 then ([unit_price] - [unit_cost]) / [unit_price] else 0,
        Percentage.Type
    ),

    #"Added Price Tier" = Table.AddColumn(#"Added Profit Margin", "Price Tier", each
        if [unit_price] >= 1000 then "Premium"
        else if [unit_price] >= 500 then "Mid-Range"
        else if [unit_price] >= 100 then "Standard"
        else "Budget",
        type text
    ),

    #"Removed Duplicates" = Table.Distinct(#"Added Price Tier", {"product_id"}),

    #"Renamed Columns" = Table.RenameColumns(#"Removed Duplicates", {
        {"product_id", "Product ID"},
        {"product_name", "Product Name"},
        {"category", "Category"},
        {"sub_category", "Sub-Category"},
        {"unit_price", "Unit Price"},
        {"unit_cost", "Unit Cost"}
    })
in
    #"Renamed Columns"
