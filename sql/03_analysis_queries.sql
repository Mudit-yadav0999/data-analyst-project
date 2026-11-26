-- =====================================================================
-- 03_analysis_queries.sql : business analysis (Oracle 12c+ syntax)
-- Concepts covered: JOIN, GROUP BY, HAVING, subquery, CTE, window functions
-- =====================================================================

-- ---------------------------------------------------------------------
-- Q1. Headline KPIs (JOIN + aggregation)
-- ---------------------------------------------------------------------
SELECT ROUND(SUM(oi.sales), 2)                              AS total_sales,
       ROUND(SUM(oi.profit), 2)                             AS total_profit,
       COUNT(DISTINCT oi.order_id)                          AS total_orders,
       SUM(oi.quantity)                                     AS total_quantity,
       ROUND(SUM(oi.profit) / SUM(oi.sales) * 100, 2)       AS profit_margin_pct,
       ROUND(SUM(oi.sales) / COUNT(DISTINCT oi.order_id), 2) AS avg_order_value
FROM   order_items oi
JOIN   orders o ON o.order_id = oi.order_id;

-- ---------------------------------------------------------------------
-- Q2. Yearly performance + YoY growth (CTE + LAG)
-- ---------------------------------------------------------------------
WITH yearly AS (
    SELECT EXTRACT(YEAR FROM o.order_date) AS yr,
           SUM(oi.sales)                   AS sales,
           SUM(oi.profit)                  AS profit,
           COUNT(DISTINCT o.order_id)      AS orders
    FROM   orders o
    JOIN   order_items oi ON oi.order_id = o.order_id
    GROUP  BY EXTRACT(YEAR FROM o.order_date)
)
SELECT yr,
       ROUND(sales, 2)  AS sales,
       ROUND(profit, 2) AS profit,
       orders,
       ROUND((sales - LAG(sales) OVER (ORDER BY yr))
             / NULLIF(LAG(sales) OVER (ORDER BY yr), 0) * 100, 2) AS yoy_growth_pct
FROM   yearly
ORDER  BY yr;

-- ---------------------------------------------------------------------
-- Q3. Monthly sales, MoM growth and running total (CTE + window functions)
-- ---------------------------------------------------------------------
WITH monthly AS (
    SELECT TRUNC(o.order_date, 'MM') AS month_start,
           SUM(oi.sales)             AS sales,
           SUM(oi.profit)            AS profit,
           COUNT(DISTINCT o.order_id) AS orders
    FROM   orders o
    JOIN   order_items oi ON oi.order_id = o.order_id
    GROUP  BY TRUNC(o.order_date, 'MM')
)
SELECT TO_CHAR(month_start, 'YYYY-MM')                      AS month,
       ROUND(sales, 2)                                      AS sales,
       ROUND(profit, 2)                                     AS profit,
       orders,
       ROUND((sales - LAG(sales) OVER (ORDER BY month_start))
             / NULLIF(LAG(sales) OVER (ORDER BY month_start), 0) * 100, 2) AS mom_growth_pct,
       ROUND(SUM(sales) OVER (ORDER BY month_start), 2)     AS running_total_sales
FROM   monthly
ORDER  BY month_start;

-- ---------------------------------------------------------------------
-- Q4. Top 10 products by sales (RANK; ties handled correctly)
-- ---------------------------------------------------------------------
SELECT *
FROM  (SELECT p.product_name,
              p.category,
              ROUND(SUM(oi.sales), 2)  AS sales,
              ROUND(SUM(oi.profit), 2) AS profit,
              RANK() OVER (ORDER BY SUM(oi.sales) DESC) AS sales_rank
       FROM   order_items oi
       JOIN   products p ON p.product_id = oi.product_id
       GROUP  BY p.product_name, p.category)
WHERE  sales_rank <= 10
ORDER  BY sales_rank;

-- ---------------------------------------------------------------------
-- Q5. Best product inside every category (ROW_NUMBER + PARTITION BY)
-- ---------------------------------------------------------------------
WITH product_sales AS (
    SELECT p.category, p.product_name, SUM(oi.sales) AS sales
    FROM   order_items oi
    JOIN   products p ON p.product_id = oi.product_id
    GROUP  BY p.category, p.product_name
), ranked AS (
    SELECT ps.*, ROW_NUMBER() OVER (PARTITION BY category ORDER BY sales DESC) AS rn
    FROM   product_sales ps
)
SELECT category, product_name, ROUND(sales, 2) AS sales
FROM   ranked
WHERE  rn <= 3
ORDER  BY category, rn;

-- ---------------------------------------------------------------------
-- Q6. Region-wise performance with share of total (RATIO_TO_REPORT)
-- ---------------------------------------------------------------------
SELECT o.region,
       ROUND(SUM(oi.sales), 2)                                  AS sales,
       ROUND(SUM(oi.profit), 2)                                 AS profit,
       COUNT(DISTINCT o.order_id)                               AS orders,
       ROUND(SUM(oi.profit) / SUM(oi.sales) * 100, 2)           AS margin_pct,
       ROUND(RATIO_TO_REPORT(SUM(oi.sales)) OVER () * 100, 2)   AS sales_share_pct
FROM   orders o
JOIN   order_items oi ON oi.order_id = o.order_id
GROUP  BY o.region
ORDER  BY sales DESC;

-- ---------------------------------------------------------------------
-- Q7. Category / sub-category profitability (GROUP BY + HAVING)
--     HAVING: sirf wo sub-categories jo loss mein hain
-- ---------------------------------------------------------------------
SELECT p.category,
       p.sub_category,
       ROUND(SUM(oi.sales), 2)  AS sales,
       ROUND(SUM(oi.profit), 2) AS profit,
       ROUND(SUM(oi.profit) / SUM(oi.sales) * 100, 2) AS margin_pct
FROM   order_items oi
JOIN   products p ON p.product_id = oi.product_id
GROUP  BY p.category, p.sub_category
HAVING SUM(oi.profit) < 0
ORDER  BY profit;

-- Full category view (all rows)
SELECT p.category,
       ROUND(SUM(oi.sales), 2)  AS sales,
       ROUND(SUM(oi.profit), 2) AS profit,
       ROUND(SUM(oi.profit) / SUM(oi.sales) * 100, 2) AS margin_pct
FROM   order_items oi
JOIN   products p ON p.product_id = oi.product_id
GROUP  BY p.category
ORDER  BY sales DESC;

-- ---------------------------------------------------------------------
-- Q8. Customers who spent more than the average customer (SUBQUERY)
-- ---------------------------------------------------------------------
SELECT c.customer_id, c.customer_name, c.segment,
       ROUND(SUM(oi.sales), 2) AS total_spent
FROM   customers c
JOIN   orders o       ON o.customer_id = c.customer_id
JOIN   order_items oi ON oi.order_id   = o.order_id
GROUP  BY c.customer_id, c.customer_name, c.segment
HAVING SUM(oi.sales) > (SELECT AVG(cust_total)
                        FROM  (SELECT SUM(oi2.sales) AS cust_total
                               FROM   orders o2
                               JOIN   order_items oi2 ON oi2.order_id = o2.order_id
                               GROUP  BY o2.customer_id))
ORDER  BY total_spent DESC
FETCH FIRST 15 ROWS ONLY;

-- ---------------------------------------------------------------------
-- Q9. Customer value tiers (CTE + NTILE)
-- ---------------------------------------------------------------------
WITH cust AS (
    SELECT o.customer_id,
           SUM(oi.sales)              AS sales,
           COUNT(DISTINCT o.order_id) AS orders
    FROM   orders o
    JOIN   order_items oi ON oi.order_id = o.order_id
    GROUP  BY o.customer_id
)
SELECT CASE tier WHEN 1 THEN 'Platinum (top 20%)' WHEN 2 THEN 'Gold' WHEN 3 THEN 'Silver'
                 WHEN 4 THEN 'Bronze' ELSE 'Low' END AS customer_tier,
       COUNT(*)                 AS customers,
       ROUND(SUM(sales), 2)     AS sales,
       ROUND(AVG(orders), 1)    AS avg_orders
FROM  (SELECT cust.*, NTILE(5) OVER (ORDER BY sales DESC) AS tier FROM cust)
GROUP BY tier
ORDER BY tier;

-- ---------------------------------------------------------------------
-- Q10. Discount impact on profit (CASE + GROUP BY)
-- ---------------------------------------------------------------------
SELECT CASE WHEN discount = 0    THEN '0%'
            WHEN discount <= 0.10 THEN '1-10%'
            WHEN discount <= 0.20 THEN '11-20%'
            WHEN discount <= 0.30 THEN '21-30%'
            ELSE '>30%' END                                  AS discount_band,
       COUNT(*)                                              AS line_items,
       ROUND(SUM(sales), 2)                                  AS sales,
       ROUND(SUM(profit), 2)                                 AS profit,
       ROUND(SUM(profit) / SUM(sales) * 100, 2)              AS margin_pct
FROM   order_items
GROUP  BY CASE WHEN discount = 0    THEN '0%'
               WHEN discount <= 0.10 THEN '1-10%'
               WHEN discount <= 0.20 THEN '11-20%'
               WHEN discount <= 0.30 THEN '21-30%'
               ELSE '>30%' END
ORDER  BY MIN(discount);

-- ---------------------------------------------------------------------
-- Q11. Segment and payment-mode performance
-- ---------------------------------------------------------------------
SELECT c.segment,
       ROUND(SUM(oi.sales), 2)  AS sales,
       ROUND(SUM(oi.profit), 2) AS profit,
       COUNT(DISTINCT o.order_id) AS orders
FROM   customers c
JOIN   orders o       ON o.customer_id = c.customer_id
JOIN   order_items oi ON oi.order_id   = o.order_id
GROUP  BY c.segment
ORDER  BY sales DESC;

SELECT o.payment_mode,
       COUNT(DISTINCT o.order_id) AS orders,
       ROUND(SUM(oi.sales), 2)    AS sales,
       ROUND(RATIO_TO_REPORT(SUM(oi.sales)) OVER () * 100, 2) AS sales_share_pct
FROM   orders o
JOIN   order_items oi ON oi.order_id = o.order_id
GROUP  BY o.payment_mode
ORDER  BY sales DESC;

-- ---------------------------------------------------------------------
-- Q12. Best month per year (window: RANK partitioned by year)
-- ---------------------------------------------------------------------
WITH m AS (
    SELECT EXTRACT(YEAR FROM o.order_date)  AS yr,
           EXTRACT(MONTH FROM o.order_date) AS mn,
           SUM(oi.sales)                    AS sales
    FROM   orders o JOIN order_items oi ON oi.order_id = o.order_id
    GROUP  BY EXTRACT(YEAR FROM o.order_date), EXTRACT(MONTH FROM o.order_date)
)
SELECT yr, mn, ROUND(sales, 2) AS sales
FROM  (SELECT m.*, RANK() OVER (PARTITION BY yr ORDER BY sales DESC) AS rk FROM m)
WHERE  rk = 1
ORDER  BY yr;

-- ---------------------------------------------------------------------
-- Q13. Flat reporting view : Power BI isse connect kar sakta hai
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_sales_flat AS
SELECT oi.row_id,
       o.order_id,
       o.order_date,
       o.ship_date,
       o.ship_mode,
       o.payment_mode,
       o.region, o.state, o.city,
       c.customer_id, c.customer_name, c.segment,
       p.product_id, p.product_name, p.category, p.sub_category,
       oi.sales, oi.quantity, oi.discount, oi.profit
FROM   order_items oi
JOIN   orders      o ON o.order_id    = oi.order_id
JOIN   customers   c ON c.customer_id = o.customer_id
JOIN   products    p ON p.product_id  = oi.product_id;
