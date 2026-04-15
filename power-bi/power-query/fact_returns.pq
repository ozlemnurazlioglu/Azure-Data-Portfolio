// Power Query (M) — fact_returns transformation

let
    Source = Csv.Document(
        File.Contents("fact_returns.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.None]
    ),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),

    #"Changed Types" = Table.TransformColumnTypes(#"Promoted Headers", {
        {"return_id", type text},
        {"original_order_id", type text},
        {"return_date", type date},
        {"product_id", type text},
        {"quantity", Int64.Type},
        {"reason", type text},
        {"refund_amount", Currency.Type}
    }),

    #"Filtered Valid" = Table.SelectRows(#"Changed Types", each
        [refund_amount] > 0 and [quantity] > 0
    ),

    #"Added Return Category" = Table.AddColumn(#"Filtered Valid", "Return Category", each
        if [reason] = "Defective" or [reason] = "Quality Issue" then "Quality"
        else if [reason] = "Damaged in Shipping" then "Shipping"
        else "Customer Decision",
        type text
    ),

    #"Renamed Columns" = Table.RenameColumns(#"Added Return Category", {
        {"return_id", "Return ID"},
        {"original_order_id", "Original Order ID"},
        {"return_date", "Return Date"},
        {"product_id", "Product ID"},
        {"quantity", "Return Quantity"},
        {"reason", "Return Reason"},
        {"refund_amount", "Refund Amount"}
    })
in
    #"Renamed Columns"
