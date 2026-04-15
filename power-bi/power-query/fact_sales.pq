// Power Query (M) — fact_sales transformation
// Source: CSV file or Azure Data Lake Gen2

let
    Source = Csv.Document(
        File.Contents("fact_sales.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.None]
    ),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),

    #"Changed Types" = Table.TransformColumnTypes(#"Promoted Headers", {
        {"order_id", type text},
        {"order_date", type date},
        {"ship_date", type date},
        {"customer_id", type text},
        {"product_id", type text},
        {"rep_id", type text},
        {"channel", type text},
        {"payment_method", type text},
        {"quantity", Int64.Type},
        {"unit_price", Currency.Type},
        {"discount_pct", Percentage.Type},
        {"total_amount", Currency.Type},
        {"cost_amount", Currency.Type},
        {"profit", Currency.Type}
    }),

    #"Filtered Valid Rows" = Table.SelectRows(#"Changed Types", each
        [quantity] > 0 and [total_amount] > 0
    ),

    #"Added Shipping Days" = Table.AddColumn(#"Filtered Valid Rows", "Shipping Days", each
        Duration.Days([ship_date] - [order_date]),
        Int64.Type
    ),

    #"Added Net Amount" = Table.AddColumn(#"Added Shipping Days", "Net Amount", each
        [total_amount] - ([total_amount] * [discount_pct]),
        Currency.Type
    ),

    #"Added Discount Flag" = Table.AddColumn(#"Added Net Amount", "Has Discount", each
        [discount_pct] > 0,
        type logical
    ),

    #"Added Discount Tier" = Table.AddColumn(#"Added Discount Flag", "Discount Tier", each
        if [discount_pct] = 0 then "No Discount"
        else if [discount_pct] <= 0.05 then "1-5%"
        else if [discount_pct] <= 0.10 then "6-10%"
        else if [discount_pct] <= 0.15 then "11-15%"
        else if [discount_pct] <= 0.20 then "16-20%"
        else "20%+",
        type text
    ),

    #"Removed Duplicates" = Table.Distinct(#"Added Discount Tier", {"order_id"}),

    #"Renamed Columns" = Table.RenameColumns(#"Removed Duplicates", {
        {"order_id", "Order ID"},
        {"order_date", "Order Date"},
        {"ship_date", "Ship Date"},
        {"customer_id", "Customer ID"},
        {"product_id", "Product ID"},
        {"rep_id", "Rep ID"},
        {"channel", "Channel"},
        {"payment_method", "Payment Method"},
        {"quantity", "Quantity"},
        {"unit_price", "Unit Price"},
        {"discount_pct", "Discount %"},
        {"total_amount", "Total Amount"},
        {"cost_amount", "Cost Amount"},
        {"profit", "Profit"}
    })
in
    #"Renamed Columns"
