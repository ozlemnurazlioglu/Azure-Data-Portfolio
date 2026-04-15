// Power Query (M) — dim_date transformation
// Mark as Date Table in Power BI for time intelligence functions

let
    Source = Csv.Document(
        File.Contents("dim_date.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.None]
    ),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),

    #"Changed Types" = Table.TransformColumnTypes(#"Promoted Headers", {
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

    #"Added Month Sort" = Table.AddColumn(#"Changed Types", "MonthSort", each [month], Int64.Type),

    #"Added Day Sort" = Table.AddColumn(#"Added Month Sort", "DaySort", each
        if [day_of_week] = "Monday" then 1
        else if [day_of_week] = "Tuesday" then 2
        else if [day_of_week] = "Wednesday" then 3
        else if [day_of_week] = "Thursday" then 4
        else if [day_of_week] = "Friday" then 5
        else if [day_of_week] = "Saturday" then 6
        else 7,
        Int64.Type
    ),

    #"Added Year-Month" = Table.AddColumn(#"Added Day Sort", "Year-Month", each
        Text.From([year]) & "-" & Text.PadStart(Text.From([month]), 2, "0"),
        type text
    ),

    #"Added Year-Quarter" = Table.AddColumn(#"Added Year-Month", "Year-Quarter", each
        Text.From([year]) & "-" & [quarter],
        type text
    ),

    #"Added Is Holiday" = Table.AddColumn(#"Added Year-Quarter", "IsHolidaySeason", each
        if [month] >= 11 and [month] <= 12 then true else false,
        type logical
    ),

    #"Renamed Columns" = Table.RenameColumns(#"Added Is Holiday", {
        {"full_date", "Date"},
        {"year", "Year"},
        {"quarter", "Quarter"},
        {"month", "Month Number"},
        {"month_name", "Month"},
        {"day_of_week", "Day of Week"},
        {"is_weekend", "Is Weekend"},
        {"fiscal_year", "Fiscal Year"},
        {"fiscal_quarter", "Fiscal Quarter"}
    })
in
    #"Renamed Columns"
