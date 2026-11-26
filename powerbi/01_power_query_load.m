// Power BI > Home > Transform data > New Source > Blank Query > Advanced Editor > paste this.
// Change the path to your own folder. Query name: Sales
let
    Source   = Csv.Document(File.Contents("C:\Projects\Sales-Performance-Dashboard\data\cleaned\sales_cleaned.csv"),
                            [Delimiter=",", Columns=28, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed    = Table.TransformColumnTypes(Promoted, {
        {"Row ID", Int64.Type}, {"Order ID", type text}, {"Order Date", type date}, {"Ship Date", type date},
        {"Ship Mode", type text}, {"Customer ID", type text}, {"Customer Name", type text}, {"Segment", type text},
        {"Country", type text}, {"City", type text}, {"State", type text}, {"Region", type text},
        {"Product ID", type text}, {"Category", type text}, {"Sub-Category", type text}, {"Product Name", type text},
        {"Sales", Currency.Type}, {"Quantity", Int64.Type}, {"Discount", Percentage.Type}, {"Profit", Currency.Type},
        {"Payment Mode", type text}, {"Year", Int64.Type}, {"Month Start", type date}, {"Month Name", type text},
        {"Month Number", Int64.Type}, {"Quarter", type text}, {"Ship Days", Int64.Type}, {"Profit Margin %", type number}}, "en-US")
in
    Typed

// ---------------------------------------------------------------
// ORACLE alternative: Get Data > Oracle Database
//   Server : localhost:1521/XEPDB1   (Oracle Client / ODP.NET must be installed)
//   Advanced > SQL statement:  SELECT * FROM vw_sales_flat
// The view vw_sales_flat is created in sql/03_analysis_queries.sql (Q13).
// Column names will then be UPPER_CASE (ORDER_DATE, SALES ...): rename or adjust the DAX accordingly.
// ---------------------------------------------------------------
