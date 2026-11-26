-- =====================================================================
-- Sales Performance Dashboard | Oracle SQL
-- 01_create_tables.sql : schema (4 normalised tables)
-- Run as the project user in SQL Developer / SQL*Plus
-- =====================================================================

-- Re-runnable: drop in child -> parent order
BEGIN
  FOR t IN (SELECT table_name FROM user_tables
             WHERE table_name IN ('ORDER_ITEMS','ORDERS','PRODUCTS','CUSTOMERS')) LOOP
    EXECUTE IMMEDIATE 'DROP TABLE ' || t.table_name || ' CASCADE CONSTRAINTS PURGE';
  END LOOP;
END;
/

CREATE TABLE customers (
    customer_id    VARCHAR2(10)   NOT NULL,
    customer_name  VARCHAR2(100)  NOT NULL,
    segment        VARCHAR2(20)   NOT NULL,
    CONSTRAINT pk_customers PRIMARY KEY (customer_id),
    CONSTRAINT ck_segment CHECK (segment IN ('Consumer','Corporate','Home Office'))
);

CREATE TABLE products (
    product_id     VARCHAR2(20)   NOT NULL,
    product_name   VARCHAR2(150)  NOT NULL,
    category       VARCHAR2(30)   NOT NULL,
    sub_category   VARCHAR2(30)   NOT NULL,
    CONSTRAINT pk_products PRIMARY KEY (product_id),
    CONSTRAINT ck_category CHECK (category IN ('Furniture','Office Supplies','Technology'))
);

CREATE TABLE orders (
    order_id       VARCHAR2(20)   NOT NULL,
    order_date     DATE           NOT NULL,
    ship_date      DATE           NOT NULL,
    ship_mode      VARCHAR2(20)   NOT NULL,
    customer_id    VARCHAR2(10)   NOT NULL,
    region         VARCHAR2(10)   NOT NULL,
    state          VARCHAR2(40)   NOT NULL,
    city           VARCHAR2(40)   NOT NULL,
    payment_mode   VARCHAR2(20)   NOT NULL,
    CONSTRAINT pk_orders PRIMARY KEY (order_id),
    CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id) REFERENCES customers (customer_id),
    CONSTRAINT ck_region CHECK (region IN ('East','West','Central','South')),
    CONSTRAINT ck_ship_after_order CHECK (ship_date >= order_date)
);

CREATE TABLE order_items (
    row_id         NUMBER(10)     NOT NULL,
    order_id       VARCHAR2(20)   NOT NULL,
    product_id     VARCHAR2(20)   NOT NULL,
    sales          NUMBER(12,2)   NOT NULL,
    quantity       NUMBER(5)      NOT NULL,
    discount       NUMBER(3,2)    DEFAULT 0 NOT NULL,
    profit         NUMBER(12,2)   NOT NULL,
    CONSTRAINT pk_order_items PRIMARY KEY (row_id),
    CONSTRAINT fk_items_order   FOREIGN KEY (order_id)   REFERENCES orders (order_id),
    CONSTRAINT fk_items_product FOREIGN KEY (product_id) REFERENCES products (product_id),
    CONSTRAINT ck_sales_positive CHECK (sales > 0),
    CONSTRAINT ck_qty_positive   CHECK (quantity > 0),
    CONSTRAINT ck_discount_range CHECK (discount BETWEEN 0 AND 1)
);

-- Indexes for join / filter columns
CREATE INDEX ix_orders_date      ON orders (order_date);
CREATE INDEX ix_orders_customer  ON orders (customer_id);
CREATE INDEX ix_orders_region    ON orders (region);
CREATE INDEX ix_items_order      ON order_items (order_id);
CREATE INDEX ix_items_product    ON order_items (product_id);
