# 02 - Cleaned data Oracle mein load karna

Load order **parent -> child** rakho: customers, products, orders, order_items.

## Option A: SQL Developer (beginner ke liye easiest)
1. Left panel mein table par right-click -> **Import Data...**
2. `data/cleaned/<table>.csv` select karo (customers -> products -> orders -> order_items).
3. Header = checked, Format = CSV.
4. **orders** ke liye date columns mein format `YYYY-MM-DD` set karo.
5. Finish -> Commit.

## Option B: SQL*Loader (command line)
CSV files aur `.ctl` files ek hi folder mein copy karo, phir:

```
sqlldr userid=SALES_USER/password@//localhost:1521/XEPDB1 control=customers.ctl   log=customers.log
sqlldr userid=SALES_USER/password@//localhost:1521/XEPDB1 control=products.ctl    log=products.log
sqlldr userid=SALES_USER/password@//localhost:1521/XEPDB1 control=orders.ctl      log=orders.log
sqlldr userid=SALES_USER/password@//localhost:1521/XEPDB1 control=order_items.ctl log=order_items.log
```

## Load ke baad row counts (expected)
| Table | Rows |
|---|---|
| customers | 800 |
| products | 42 |
| orders | 4497 |
| order_items | 9966 |
