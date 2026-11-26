# Data Dictionary (cleaned dataset: `data/cleaned/sales_cleaned.csv`)

| Column | Type | Description |
|---|---|---|
| Row ID | int | Unique order-line id |
| Order ID | text | Order id (one order has 1-5 lines) |
| Order Date / Ship Date | date | Dates (ISO `YYYY-MM-DD` in cleaned files) |
| Ship Mode | text | Standard Class, Second Class, First Class, Same Day |
| Customer ID / Customer Name | text | Customer identifiers |
| Segment | text | Consumer, Corporate, Home Office |
| Country, State, City | text | Delivery location |
| Region | text | East, West, Central, South |
| Product ID / Product Name | text | Product identifiers |
| Category / Sub-Category | text | 3 categories, 13 sub-categories |
| Sales | decimal | Revenue after discount (> 0) |
| Quantity | int | Units (> 0) |
| Discount | decimal | 0 to 1 (e.g. 0.20 = 20%) |
| Profit | decimal | Profit for the line (can be negative) |
| Payment Mode | text | Credit Card, Debit Card, UPI, Net Banking, Cash on Delivery, PayPal, Unknown (synthetic column) |
| Year, Quarter, Month Start, Month Name, Month Number | derived | Time attributes |
| Ship Days | int | Ship Date - Order Date |
| Profit Margin % | decimal | Profit / Sales x 100 for the line |

## Cleaning rules applied (see `data/cleaned/cleaning_log.csv`)
| Problem in raw data | Count | Rule |
|---|---|---|
| Exact duplicate rows | 60 | Removed |
| Category / Region casing & spaces (`TECHNOLOGY`, `furniture `, `west`) | ~145 | Trim + Title Case; Category re-derived from Sub-Category |
| Invalid / future order dates | 6 | 4 recovered from other lines of the same order, 2 removed |
| Negative or zero Sales | 18 | Removed (data-entry errors) |
| Missing Customer Name / Segment | ~65 | Filled from Customer ID master (1 unrecoverable name labelled `Unknown Customer`) |
| Missing Region | 20 | Filled from State |
| Missing Payment Mode | 40 | Filled from other lines of same order, else `Unknown` |
| Missing Discount | 25 | Set to 0 |
| Missing Profit | 8 | Removed (cannot be estimated reliably) |

Counts are approximate injected-issue counts in the raw file.

Result: **10,054 raw rows -> 9,966 clean rows**.
