OPTIONS (SKIP=1)
LOAD DATA
INFILE 'products.csv'
APPEND INTO TABLE products
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' TRAILING NULLCOLS
(product_id, product_name, category, sub_category)
