# Power BI Dashboard: Step-by-Step Build Guide (Hinglish)

> `.pbix` file Power BI Desktop (Windows) mein hi ban sakti hai, isliye is repo mein uska **exact blueprint** diya hai.
> Follow karoge to ~45-60 minute mein dashboard ready. Phir **File > Save As** `powerbi/Sales_Performance_Dashboard.pbix`.

## Step 1: Data load
1. Power BI Desktop kholo > **Home > Get data > Text/CSV** > `data/cleaned/sales_cleaned.csv` > **Transform Data**.
   (Ya `01_power_query_load.m` paste karo.) Table ka naam **Sales** rakho.
2. Data types check karo: Order Date = Date, Sales/Profit = Currency, Discount = Percentage.
3. **Close & Apply**.

> Oracle se connect karna ho: **Get data > Oracle database** > `SELECT * FROM vw_sales_flat`.

## Step 2: Date table + relationship
1. **Modeling > New table**: `02_dax_measures.dax` ka section 0 (`Date = ...`) paste karo.
2. Table tools > **Mark as date table** > `Date[Date]`.
3. `Date[Month]` select karo > Column tools > **Sort by column** > `Month No`.
4. Model view mein `Date[Date]` ko `Sales[Order Date]` se drag karo (one-to-many).

## Step 3: Measures
Ek blank table `_Measures` banao (Enter data > blank). `02_dax_measures.dax` ke sab measures wahin banao.

## Step 4: Hierarchies (drill-down ke liye)
- **Product hierarchy:** Sales[Category] > Sales[Sub-Category] > Sales[Product Name]
- **Date hierarchy:** Date[Year] > Date[Quarter] > Date[Month]
- **Geography hierarchy:** Sales[Region] > Sales[State] > Sales[City]
(Fields pane mein column pe right-click > *New hierarchy*, ya ek column dusre pe drag karo.)

## Step 5: Theme
**View > Themes > Browse for themes** > `theme_sales_dashboard.json`. Page size: **16:9** (1280 x 720).

## Step 6: Page layout (1280 x 720)

```
+-----------------------------------------------------------------------------------+
|  SALES PERFORMANCE DASHBOARD                      [Date slicer: Between]          |
|  [Category dd] [Region dd] [Segment buttons]                      [Reset button]  |
+-----------------------------------------------------------------------------------+
| [Total Sales] [Total Profit] [Total Orders] [Total Qty] [Profit Margin %]  (cards)|
+-------------------------------------------+---------------------------------------+
|  Monthly Sales Trend (line + Profit)      |  Sales by Category (clustered bar)    |
|  x: Date hierarchy, y: Total Sales        |  y: Category, x: Total Sales          |
+---------------------------+---------------+---------------------------------------+
|  Sales by Region (map)    | Top 10 Products by Sales (bar)  | Profit vs Sales     |
|  Location: State          | Top N filter = 10 by Total Sales| scatter (by Product)|
+---------------------------+---------------------------------+---------------------+
```

### Visual by visual

| # | Visual | Fields | Settings |
|---|---|---|---|
| 1-5 | **Card** x5 | `Total Sales`, `Total Profit`, `Total Orders`, `Total Quantity`, `Profit Margin %` | Format: $ / % ; Margin card: fx > font colour > Field value > `Margin Color` ; Sales card: add `KPI Subtitle Sales` as reference label |
| 6 | **Line chart** | X: Date hierarchy (Year > Quarter > Month), Y: `Total Sales`, Secondary: `Total Profit` | Title fx > `Title Monthly Trend`; turn on drill-down arrows |
| 7 | **Clustered bar** | Y: Category (hierarchy), X: `Total Sales`, Tooltips: `Total Profit`, `Profit Margin %` | Title: "Sales by Category | drill to Sub-Category" |
| 8 | **Filled map** (or bar chart) | Location: State, Size/Saturation: `Total Sales`, Tooltips: `Total Profit`, `Total Orders` | Location data category = State or Province; Country = United States. Title fx > `Title Region`. Backup: clustered bar by Region |
| 9 | **Bar chart** | Y: Product Name, X: `Total Sales` | Filters pane > Product Name > **Top N** > Top 10 > By value `Total Sales`. Sort descending. Title fx > `Title Top Products` |
| 10 | **Scatter** | Details: Product Name, X: `Total Sales`, Y: `Total Profit`, Colour: Category | Add constant line y = 0: loss-making products niche dikhenge |
| 11 | **Slicer** Date | `Date[Date]` | Style = *Between* |
| 12 | **Slicer** Category | `Sales[Category]` | Dropdown |
| 13 | **Slicer** Region | `Sales[Region]` | Dropdown / tile |
| 14 | **Slicer** Segment | `Sales[Segment]` | Tile buttons |

## Step 7: Dynamic titles
Visual select > Format > **Title > Text > fx** > *Format style: Field value* > measure choose (`Title Monthly Trend` etc.).
Slicer change karte hi title badal jaata hai, e.g. "Monthly Sales Trend | Technology | West".

## Step 8: Tooltip page (report-page tooltip)
1. New page > Format page > **Page information > Allow use as tooltip = On**; Page size = *Tooltip*.
2. Usme `Total Sales`, `Total Profit`, `Profit Margin %`, `Tooltip Orders Text` aur ek chhota bar chart (Sub-Category) daalo.
3. Main page ke visuals > Format > **Tooltips > Type: Report page** > yeh page select karo.

## Step 9: Interactions
- **Cross-filtering:** default ON. Kisi bar/map pe click karo to baaki sab visuals filter hote hain.
- **Edit interactions** (Format > Edit interactions): KPI cards ko Line chart se *Filter* mode mein rakho; Top-10 bar ko map se *Filter*.
- **Drill-down:** Category chart pe *drill mode* arrow > Sub-Category > Product.
- **Reset button:** Insert > Buttons > Bookmark; pehle sab slicers clear karke bookmark "Reset" banao, button ko link karo.

## Step 10: Final polish checklist
- [ ] Sab visuals ke titles dynamic ya meaningful
- [ ] Fonts/colours theme se
- [ ] Numbers formatted ($, %, K/M)
- [ ] Mobile layout (View > Mobile layout) optional
- [ ] Alt text on visuals (accessibility)
- [ ] File saved, screenshot `images/dashboard_preview.png` README ke liye

## Step 11: Acceptance test
`docs/test_results.md` ke last table mein reference values hain. Slicers set karo (e.g. Region = West, Category = Technology, Year = 2024) aur dekho ki cards **239,476.02 / 57,328.83 / 194 / 777 / 23.94%** dikhate hain. Poora checklist `docs/testing_and_acceptance.md` mein hai.
