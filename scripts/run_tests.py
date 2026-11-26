"""
Automated tests:
  A) Data-quality tests on cleaned data
  B) SQL-logic tests: the same JOIN/GROUP BY/CTE/window logic as sql/03_analysis_queries.sql,
     executed on SQLite (Oracle is not available in this environment) and compared with pandas.
  C) Reference numbers for manual Power BI filter tests
Writes docs/test_results.md
"""
import json, sqlite3
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
C = ROOT / "data" / "cleaned"
df = pd.read_csv(C / "sales_cleaned.csv", parse_dates=["Order Date", "Ship Date"])
exp = json.load(open(ROOT / "docs" / "expected_kpis.json"))["kpis"]
results = []
def check(name, cond, detail=""):
    results.append((name, "PASS" if cond else "FAIL", detail))

# ---------- A. data-quality ----------
check("A1 No duplicate order lines", not df.duplicated(["Row ID"]).any() and not df.drop(columns=["Row ID"]).duplicated().any())
check("A2 No missing values", int(df.isna().sum().sum()) == 0, f"nulls={int(df.isna().sum().sum())}")
check("A3 No negative/zero sales", (df["Sales"] > 0).all(), f"min sales={df['Sales'].min()}")
check("A4 Valid dates (<= 2026-11-26, ship >= order)", (df["Order Date"] <= "2026-11-26").all() and (df["Ship Date"] >= df["Order Date"]).all())
check("A5 Exactly 3 clean categories", sorted(df["Category"].unique()) == ["Furniture", "Office Supplies", "Technology"], str(sorted(df["Category"].unique())))
check("A6 Exactly 4 clean regions", sorted(df["Region"].unique()) == ["Central", "East", "South", "West"])
check("A7 Discount within 0..1, Quantity > 0", df["Discount"].between(0, 1).all() and (df["Quantity"] > 0).all())
check("A8 Sum(regions) == Sum(categories) == grand total",
      abs(df.groupby("Region")["Sales"].sum().sum() - df.groupby("Category")["Sales"].sum().sum()) < 0.01 and abs(df["Sales"].sum() - exp["total_sales"]) < 0.01)
check("A9 Profit margin = profit / sales", abs(df["Profit"].sum() / df["Sales"].sum() * 100 - exp["profit_margin_pct"]) < 0.01)
orders_ok = all(df.groupby("Order ID")[c].nunique().max() == 1 for c in ["Order Date", "Customer ID", "Region", "Payment Mode"])
check("A10 One order = one date/customer/region/payment", orders_ok)

# ---------- B. SQL logic on SQLite ----------
con = sqlite3.connect(":memory:")
for t in ["customers", "products", "orders", "order_items"]:
    pd.read_csv(C / f"{t}.csv").to_sql(t, con, index=False)
q = lambda s: pd.read_sql_query(s, con)

k = q("""SELECT ROUND(SUM(oi.sales),2) s, ROUND(SUM(oi.profit),2) p, COUNT(DISTINCT oi.order_id) o, SUM(oi.quantity) q,
                ROUND(SUM(oi.profit)/SUM(oi.sales)*100,2) m, ROUND(SUM(oi.sales)/COUNT(DISTINCT oi.order_id),2) aov
         FROM order_items oi JOIN orders o ON o.order_id=oi.order_id""").iloc[0]
check("B1 SQL total sales == Python", abs(k.s - exp["total_sales"]) < 0.01, f"{k.s}")
check("B2 SQL total profit == Python", abs(k.p - exp["total_profit"]) < 0.01, f"{k.p}")
check("B3 SQL orders == Python", int(k.o) == exp["total_orders"], f"{int(k.o)}")
check("B4 SQL quantity == Python", int(k.q) == exp["total_quantity"], f"{int(k.q)}")
check("B5 SQL margin % and AOV == Python", abs(k.m - exp["profit_margin_pct"]) < 0.01 and abs(k.aov - exp["avg_order_value"]) < 0.01, f"{k.m}% / {k.aov}")

top = q("""SELECT product_name, sales, sales_rank FROM (
             SELECT p.product_name, ROUND(SUM(oi.sales),2) sales, RANK() OVER (ORDER BY SUM(oi.sales) DESC) sales_rank
             FROM order_items oi JOIN products p ON p.product_id=oi.product_id GROUP BY p.product_name)
           WHERE sales_rank<=10 ORDER BY sales_rank""")
py_top = [t["product"] for t in exp["top10_products"]]
check("B6 SQL Top-10 products & order == Python", top["product_name"].tolist() == py_top)

mon = q("""WITH m AS (SELECT strftime('%Y-%m', o.order_date) mth, SUM(oi.sales) sales
                     FROM orders o JOIN order_items oi ON oi.order_id=o.order_id GROUP BY 1)
           SELECT mth, ROUND(sales,2) sales, ROUND((sales-LAG(sales) OVER (ORDER BY mth))/LAG(sales) OVER (ORDER BY mth)*100,2) mom
           FROM m ORDER BY mth""")
py_m = df.groupby(df["Order Date"].dt.strftime("%Y-%m"))["Sales"].sum().round(2)
check("B7 SQL monthly sales (48 months) == Python", len(mon) == 48 and (mon.set_index("mth")["sales"] - py_m).abs().max() < 0.01, f"months={len(mon)}")

reg = q("""SELECT o.region, ROUND(SUM(oi.sales),2) s FROM orders o JOIN order_items oi ON oi.order_id=o.order_id GROUP BY o.region""").set_index("region")["s"]
check("B8 SQL region sales == Python", (reg - df.groupby("Region")["Sales"].sum().round(2)).abs().max() < 0.01)

cat = q("""SELECT p.category, ROUND(SUM(oi.profit),2) pr FROM order_items oi JOIN products p ON p.product_id=oi.product_id GROUP BY p.category""").set_index("category")["pr"]
check("B9 SQL category profit == Python", (cat - df.groupby("Category")["Profit"].sum().round(2)).abs().max() < 0.01)

hv = q("""SELECT p.sub_category, ROUND(SUM(oi.profit),2) pr FROM order_items oi JOIN products p ON p.product_id=oi.product_id
          GROUP BY p.sub_category HAVING SUM(oi.profit) < 0""")
py_loss = df.groupby("Sub-Category")["Profit"].sum(); py_loss = py_loss[py_loss < 0]
check("B10 HAVING loss-making sub-categories == Python", set(hv["sub_category"]) == set(py_loss.index), str(sorted(hv["sub_category"])))

sub = q("""SELECT COUNT(*) n FROM (SELECT c.customer_id FROM customers c JOIN orders o ON o.customer_id=c.customer_id
            JOIN order_items oi ON oi.order_id=o.order_id GROUP BY c.customer_id
            HAVING SUM(oi.sales) > (SELECT AVG(t) FROM (SELECT SUM(oi2.sales) t FROM orders o2 JOIN order_items oi2
                                     ON oi2.order_id=o2.order_id GROUP BY o2.customer_id)))""").iloc[0, 0]
cs = df.groupby("Customer ID")["Sales"].sum()
check("B11 Subquery (customers above average) == Python", int(sub) == int((cs > cs.mean()).sum()), f"{int(sub)} customers")

orph = q("SELECT COUNT(*) n FROM order_items oi LEFT JOIN orders o ON o.order_id=oi.order_id WHERE o.order_id IS NULL").iloc[0, 0]
check("B12 No orphan order_items (FK integrity)", orph == 0)

# ---------- C. reference numbers for Power BI manual tests ----------
f1 = df[(df["Region"] == "West") & (df["Category"] == "Technology") & (df["Year"] == 2024)]
f2 = df[(df["Segment"] == "Corporate") & (df["Year"] == 2025)]
f3 = df[(df["Order Date"] >= "2025-11-01") & (df["Order Date"] <= "2025-12-31")]
f4 = df[df["Category"] == "Furniture"]
ref = [("West + Technology + 2024", f1), ("Corporate + 2025", f2), ("1-Nov-2025 to 31-Dec-2025", f3), ("Category = Furniture", f4)]

out = ["# Test Results", "", "Automated run on cleaned data (`python scripts/run_tests.py`).", "",
       "| # | Test | Result | Detail |", "|---|---|---|---|"]
for n, r, d in results:
    num, name = n.split(" ", 1)
    out.append(f"| {num} | {name} | {r} | {d} |")
passed = sum(r == "PASS" for _, r, _ in results)
out += ["", f"**{passed}/{len(results)} tests passed.**", "",
        "> Note: Section B runs the same query logic on SQLite because Oracle is not available where this project was built. "
        "Run `sql/04_validation_queries.sql` on your Oracle database for the final sign-off (query V9 should return all zeros).", "",
        "## Reference values for Power BI filter tests", "",
        "| Filter combination | Total Sales | Total Profit | Orders | Quantity | Margin % |", "|---|---|---|---|---|---|"]
for n, d in ref:
    out.append(f"| {n} | {d['Sales'].sum():,.2f} | {d['Profit'].sum():,.2f} | {d['Order ID'].nunique():,} | {int(d['Quantity'].sum()):,} | {d['Profit'].sum()/d['Sales'].sum()*100:.2f}% |")
(ROOT / "docs" / "test_results.md").write_text("\n".join(out) + "\n")
print("\n".join(out))
assert passed == len(results), "some tests failed"
