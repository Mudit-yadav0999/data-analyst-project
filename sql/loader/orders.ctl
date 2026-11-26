OPTIONS (SKIP=1)
LOAD DATA
INFILE 'orders.csv'
APPEND INTO TABLE orders
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' TRAILING NULLCOLS
(order_id,
 order_date DATE "YYYY-MM-DD",
 ship_date  DATE "YYYY-MM-DD",
 ship_mode, customer_id, region, state, city, payment_mode)
