# Test Results

Automated run on cleaned data (`python scripts/run_tests.py`).

| # | Test | Result | Detail |
|---|---|---|---|
| A1 | No duplicate order lines | PASS |  |
| A2 | No missing values | PASS | nulls=0 |
| A3 | No negative/zero sales | PASS | min sales=4.5 |
| A4 | Valid dates (<= 2026-11-26, ship >= order) | PASS |  |
| A5 | Exactly 3 clean categories | PASS | ['Furniture', 'Office Supplies', 'Technology'] |
| A6 | Exactly 4 clean regions | PASS |  |
| A7 | Discount within 0..1, Quantity > 0 | PASS |  |
| A8 | Sum(regions) == Sum(categories) == grand total | PASS |  |
| A9 | Profit margin = profit / sales | PASS |  |
| A10 | One order = one date/customer/region/payment | PASS |  |
| B1 | SQL total sales == Python | PASS | 5408541.6 |
| B2 | SQL total profit == Python | PASS | 720415.35 |
| B3 | SQL orders == Python | PASS | 4497 |
| B4 | SQL quantity == Python | PASS | 29913 |
| B5 | SQL margin % and AOV == Python | PASS | 13.32% / 1202.7 |
| B6 | SQL Top-10 products & order == Python | PASS |  |
| B7 | SQL monthly sales (48 months) == Python | PASS | months=48 |
| B8 | SQL region sales == Python | PASS |  |
| B9 | SQL category profit == Python | PASS |  |
| B10 | HAVING loss-making sub-categories == Python | PASS | ['Machines', 'Tables'] |
| B11 | Subquery (customers above average) == Python | PASS | 347 customers |
| B12 | No orphan order_items (FK integrity) | PASS |  |

**22/22 tests passed.**

> Note: Section B runs the same query logic on SQLite because Oracle is not available where this project was built. Run `sql/04_validation_queries.sql` on your Oracle database for the final sign-off (query V9 should return all zeros).

## Reference values for Power BI filter tests

| Filter combination | Total Sales | Total Profit | Orders | Quantity | Margin % |
|---|---|---|---|---|---|
| West + Technology + 2024 | 239,476.02 | 57,328.83 | 194 | 777 | 23.94% |
| Corporate + 2025 | 421,714.92 | 54,061.31 | 338 | 2,278 | 12.82% |
| 1-Nov-2025 to 31-Dec-2025 | 477,748.46 | 80,580.08 | 345 | 2,321 | 16.87% |
| Category = Furniture | 2,020,838.57 | 85,276.06 | 2,592 | 10,713 | 4.22% |
