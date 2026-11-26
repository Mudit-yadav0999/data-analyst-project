-- =====================================================================
-- 04_validation_queries.sql : data-quality + acceptance checks
-- Har query ka expected result: 0 rows / 0 count (jahan likha ho)
-- =====================================================================

-- V1. Row counts (expected: customers 800, products 42, orders 4497, order_items 9966)
SELECT 'customers' tbl, COUNT(*) cnt FROM customers UNION ALL
SELECT 'products',      COUNT(*)     FROM products  UNION ALL
SELECT 'orders',        COUNT(*)     FROM orders    UNION ALL
SELECT 'order_items',   COUNT(*)     FROM order_items;

-- V2. Duplicate order lines (expected: 0 rows)
SELECT order_id, product_id, sales, quantity, discount, profit, COUNT(*) dup_count
FROM   order_items
GROUP  BY order_id, product_id, sales, quantity, discount, profit
HAVING COUNT(*) > 1;

-- V3. NULLs in key columns (expected: 0)
SELECT COUNT(*) AS null_rows
FROM   vw_sales_flat
WHERE  order_date IS NULL OR customer_id IS NULL OR product_id IS NULL
   OR  region IS NULL OR segment IS NULL OR sales IS NULL OR profit IS NULL;

-- V4. Negative / zero sales (expected: 0)
SELECT COUNT(*) AS bad_sales FROM order_items WHERE sales <= 0;

-- V5. Invalid / out-of-range dates (expected: 0)
SELECT COUNT(*) AS bad_dates
FROM   orders
WHERE  order_date > SYSDATE OR order_date < DATE '2015-01-01' OR ship_date < order_date;

-- V6. Orphan records (expected: 0 rows)
SELECT oi.row_id FROM order_items oi LEFT JOIN orders   o ON o.order_id   = oi.order_id   WHERE o.order_id   IS NULL;
SELECT oi.row_id FROM order_items oi LEFT JOIN products p ON p.product_id = oi.product_id WHERE p.product_id IS NULL;

-- V7. Category consistency (expected: exactly 3 rows) and regions (exactly 4 rows)
SELECT category, COUNT(*) FROM products GROUP BY category;
SELECT region,   COUNT(*) FROM orders   GROUP BY region;

-- V8. Incorrect totals: sum of regions = sum of categories = grand total (expected: all 3 equal)
SELECT (SELECT ROUND(SUM(sales),2) FROM order_items)                                              AS grand_total,
       (SELECT ROUND(SUM(s),2) FROM (SELECT SUM(oi.sales) s FROM order_items oi JOIN orders o
                                      ON o.order_id = oi.order_id GROUP BY o.region))             AS sum_of_regions,
       (SELECT ROUND(SUM(s),2) FROM (SELECT SUM(oi.sales) s FROM order_items oi JOIN products p
                                      ON p.product_id = oi.product_id GROUP BY p.category))       AS sum_of_categories
FROM dual;

-- V9. ACCEPTANCE: KPI reference values from the Python notebook
--     (docs/expected_kpis.json). The difference columns should all be 0.
SELECT ROUND(SUM(sales),2)  - 5408541.60 AS diff_sales,
       ROUND(SUM(profit),2) - 720415.35  AS diff_profit,
       COUNT(DISTINCT order_id) - 4497   AS diff_orders,
       SUM(quantity) - 29913             AS diff_quantity
FROM   order_items;
