# KPI Definitions

All KPIs are calculated on the **cleaned** dataset (9,966 order lines, 4,497 orders, Jan 2022 - Dec 2025).

| KPI | Business definition | Formula (SQL) | DAX measure | Value |
|---|---|---|---|---|
| **Total Sales** | Revenue after discount, summed over all order lines | `SUM(order_items.sales)` | `SUM(Sales[Sales])` | **$5,408,541.60** |
| **Total Profit** | Sales minus cost, after discount | `SUM(order_items.profit)` | `SUM(Sales[Profit])` | **$720,415.35** |
| **Total Orders** | Number of distinct orders (an order can have many lines) | `COUNT(DISTINCT order_id)` | `DISTINCTCOUNT(Sales[Order ID])` | **4,497** |
| **Total Quantity** | Units sold | `SUM(quantity)` | `SUM(Sales[Quantity])` | **29,913** |
| **Profit Margin %** | Share of sales kept as profit | `SUM(profit) / SUM(sales) * 100` | `DIVIDE([Total Profit],[Total Sales])` | **13.32%** |
| **Average Order Value (AOV)** | Average revenue per order | `SUM(sales) / COUNT(DISTINCT order_id)` | `DIVIDE([Total Sales],[Total Orders])` | **$1,202.70** |
| **MoM Growth %** | Change in sales vs previous month | `(sales - LAG(sales)) / LAG(sales)` | `[Sales MoM %]` | per month |
| **YoY Growth %** | Change in sales vs same period last year | `(sales - LAG(sales)) / LAG(sales)` by year | `[Sales YoY %]` | 2023: +24.1%, 2024: +16.2%, 2025: +3.6% |

## Important rules
- **Never average a margin.** Margin % is always `SUM(profit) / SUM(sales)` at the selected filter level.
- **Orders are distinct counts**, never `COUNT(*)` (that would count lines).
- **Profit Margin colour rule:** red < 0%, amber 0-10%, green >= 10%.
- A "loss-making" product/sub-category means `SUM(profit) < 0` in the current filter context.
- Dates use the **Order Date** (not Ship Date) for all time analysis.
