OPTIONS (SKIP=1)
LOAD DATA
INFILE 'order_items.csv'
APPEND INTO TABLE order_items
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' TRAILING NULLCOLS
(row_id, order_id, product_id, sales, quantity, discount, profit)
