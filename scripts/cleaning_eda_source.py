# %% [markdown]
# # Sales Performance Dashboard: Data Cleaning & EDA
# **Domain:** Retail & E-commerce | **Tools:** Python (Pandas, NumPy, Matplotlib)
#
# Is notebook mein hum 5 kaam karte hain:
# 1. Raw data load + explore
# 2. Data quality checks (nulls, duplicates, negative sales, invalid dates, inconsistent categories)
# 3. Cleaning rules apply karna (har rule ka count log hota hai)
# 4. Cleaned data export (CSV for Power BI + normalized tables for Oracle)
# 5. EDA: top products, category profit, monthly trend, regional performance

# %%
import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

pd.set_option("display.max_columns", 50, "display.width", 160)
ROOT = Path.cwd()
if ROOT.name in ("notebooks", "scripts"):
    ROOT = ROOT.parent
RAW = ROOT / "data" / "raw" / "Superstore_raw.csv"
CLEAN_DIR = ROOT / "data" / "cleaned"
IMG = ROOT / "images"
CLEAN_DIR.mkdir(exist_ok=True, parents=True)
IMG.mkdir(exist_ok=True, parents=True)
TODAY = pd.Timestamp("2026-11-26")  # dates after this are impossible (future)

# %% [markdown]
# ## 1. Load & Explore

# %%
# encoding='latin-1' zaroori hai kyunki Kaggle Superstore file UTF-8 nahi hoti
df = pd.read_csv(RAW, encoding="latin-1")
df.columns = df.columns.str.strip()
print("Shape:", df.shape)
df.head()

# %%
df.info()

# %%
df.describe(include="all").T

# %% [markdown]
# ## 2. Data Quality Audit (cleaning se PEHLE)

# %%
audit = {}
audit["rows_raw"] = len(df)
audit["exact_duplicate_rows"] = int(df.duplicated().sum())
audit["null_cells_by_column"] = {k: int(v) for k, v in df.isna().sum().items() if v > 0}
audit["negative_sales_rows"] = int((df["Sales"] < 0).sum())
audit["zero_sales_rows"] = int((df["Sales"] == 0).sum())
parsed = pd.to_datetime(df["Order Date"], format="%m/%d/%Y", errors="coerce")
audit["invalid_order_dates"] = int(parsed.isna().sum())
audit["future_order_dates"] = int((parsed > TODAY).sum())
audit["category_variants_raw"] = sorted(df["Category"].dropna().unique().tolist())
audit["region_variants_raw"] = sorted(df["Region"].dropna().unique().tolist())
for k, v in audit.items():
    print(f"{k}: {v}")

# %% [markdown]
# ## 3. Cleaning (har step ka log)

# %%
log = []
def step(name, before, after):
    log.append({"step": name, "rows_before": before, "rows_after": after, "rows_affected": before - after})
    print(f"{name:<55} {before:>6} -> {after:>6}")

# 3.1 Exact duplicates
n = len(df)
df = df.drop_duplicates().copy()
step("Remove exact duplicate rows", n, len(df))

# 3.2 Standardise text columns (spaces + casing)
for c in ["Category", "Sub-Category", "Region", "Segment", "Customer Name", "Payment Mode", "Ship Mode", "State", "City"]:
    df[c] = df[c].astype("string").str.strip().str.replace(r"\s+", " ", regex=True)
for c in ["Category", "Sub-Category", "Region"]:
    df[c] = df[c].str.title()
print("Categories now:", sorted(df["Category"].dropna().unique()))
print("Regions now   :", sorted(df["Region"].dropna().unique()))

# 3.3 Category must agree with Sub-Category (one sub-category belongs to ONE category)
sub_to_cat = df.dropna(subset=["Category"]).groupby("Sub-Category")["Category"].agg(lambda s: s.mode().iat[0])
mismatch = (df["Category"] != df["Sub-Category"].map(sub_to_cat)).sum()
print("Category/Sub-Category mismatches:", int(mismatch))
df["Category"] = df["Sub-Category"].map(sub_to_cat)

# 3.4 Dates: parse strictly; recover from other lines of the same order, else drop
df["Order Date"] = pd.to_datetime(df["Order Date"], format="%m/%d/%Y", errors="coerce")
df["Ship Date"] = pd.to_datetime(df["Ship Date"], format="%m/%d/%Y", errors="coerce")
df.loc[df["Order Date"] > TODAY, "Order Date"] = pd.NaT
bad_dates = df["Order Date"].isna().sum()
sibling_date = df.groupby("Order ID")["Order Date"].transform("min")  # min ignores NaT
df["Order Date"] = df["Order Date"].fillna(sibling_date)
print(f"Invalid dates: {bad_dates}, recovered from same order: {bad_dates - df['Order Date'].isna().sum()}")
n = len(df)
df = df.dropna(subset=["Order Date"])
step("Drop rows with unrecoverable invalid Order Date", n, len(df))

# 3.5 Negative / zero sales are data-entry errors (returns are not in this feed) -> drop
n = len(df)
df = df[df["Sales"] > 0]
step("Drop rows with negative or zero Sales", n, len(df))

# 3.6 Missing values
# Customer attributes come from customer master (same Customer ID)
cust_master = df.dropna(subset=["Customer Name", "Segment"]).groupby("Customer ID").agg(
    name=("Customer Name", lambda s: s.mode().iat[0]), seg=("Segment", lambda s: s.mode().iat[0]))
df["Customer Name"] = df["Customer Name"].fillna(df["Customer ID"].map(cust_master["name"]))
df["Segment"] = df["Segment"].fillna(df["Customer ID"].map(cust_master["seg"]))
# Region from State
state_region = df.dropna(subset=["Region"]).groupby("State")["Region"].agg(lambda s: s.mode().iat[0])
df["Region"] = df["Region"].fillna(df["State"].map(state_region))
# Payment mode from other lines of same order, else 'Unknown'
order_pay = df.dropna(subset=["Payment Mode"]).groupby("Order ID")["Payment Mode"].agg(lambda s: s.mode().iat[0])
df["Payment Mode"] = df["Payment Mode"].fillna(df["Order ID"].map(order_pay)).fillna("Unknown")
# Customer with only one line and a missing name cannot be recovered -> keep the row, label it
df["Customer Name"] = df["Customer Name"].fillna("Unknown Customer")
# Discount missing -> 0 (no discount recorded)
df["Discount"] = df["Discount"].fillna(0.0)
# Profit missing cannot be guessed reliably -> drop
n = len(df)
df = df.dropna(subset=["Profit"])
step("Drop rows with missing Profit", n, len(df))
print("Remaining nulls:", int(df.isna().sum().sum()))

# 3.7 Logical checks
print("Rows where Ship Date < Order Date:", int((df["Ship Date"] < df["Order Date"]).sum()))
n = len(df)
df = df[(df["Quantity"] > 0) & (df["Discount"].between(0, 1))]
step("Drop rows with invalid Quantity/Discount", n, len(df))

# 3.8 Feature engineering
df["Year"] = df["Order Date"].dt.year
df["Month Start"] = df["Order Date"].dt.to_period("M").dt.to_timestamp()
df["Month Name"] = df["Order Date"].dt.strftime("%b")
df["Month Number"] = df["Order Date"].dt.month
df["Quarter"] = "Q" + df["Order Date"].dt.quarter.astype(str)
df["Ship Days"] = (df["Ship Date"] - df["Order Date"]).dt.days
df["Profit Margin %"] = np.round(df["Profit"] / df["Sales"] * 100, 2)
df["Sales"] = df["Sales"].round(2)
df["Profit"] = df["Profit"].round(2)
df = df.sort_values(["Order Date", "Order ID", "Row ID"]).reset_index(drop=True)

# 3.9 Order-level consistency (one order = one date/customer/payment/region)
for c in ["Order Date", "Customer ID", "Payment Mode", "Region", "Ship Mode"]:
    bad = (df.groupby("Order ID")[c].nunique() > 1).sum()
    print(f"orders with inconsistent {c}: {bad}")

# %% [markdown]
# ## 4. Export cleaned data

# %%
df.to_csv(CLEAN_DIR / "sales_cleaned.csv", index=False)

# Normalised tables for Oracle (ISO dates so TO_DATE(...,'YYYY-MM-DD') works)
customers = (df.groupby("Customer ID").agg(customer_name=("Customer Name", "first"), segment=("Segment", "first"))
               .reset_index().rename(columns={"Customer ID": "customer_id"}))
products = (df.groupby("Product ID").agg(product_name=("Product Name", "first"), category=("Category", "first"),
                                         sub_category=("Sub-Category", "first"))
              .reset_index().rename(columns={"Product ID": "product_id"}))
orders = (df.groupby("Order ID").agg(order_date=("Order Date", "min"), ship_date=("Ship Date", "min"),
                                      ship_mode=("Ship Mode", "first"), customer_id=("Customer ID", "first"),
                                      region=("Region", "first"), state=("State", "first"), city=("City", "first"),
                                      payment_mode=("Payment Mode", "first")).reset_index()
            .rename(columns={"Order ID": "order_id"}))
for c in ["order_date", "ship_date"]:
    orders[c] = orders[c].dt.strftime("%Y-%m-%d")
items = df[["Row ID", "Order ID", "Product ID", "Sales", "Quantity", "Discount", "Profit"]].copy()
items.columns = ["row_id", "order_id", "product_id", "sales", "quantity", "discount", "profit"]
for name, t in [("customers", customers), ("products", products), ("orders", orders), ("order_items", items)]:
    t.to_csv(CLEAN_DIR / f"{name}.csv", index=False)
    print(f"{name:<12} rows={len(t)}")

pd.DataFrame(log).to_csv(CLEAN_DIR / "cleaning_log.csv", index=False)

# %% [markdown]
# ## 5. KPIs (yahi numbers Oracle SQL aur Power BI se match hone chahiye)

# %%
kpi = {
    "total_sales": round(float(df["Sales"].sum()), 2),
    "total_profit": round(float(df["Profit"].sum()), 2),
    "total_orders": int(df["Order ID"].nunique()),
    "total_quantity": int(df["Quantity"].sum()),
    "profit_margin_pct": round(float(df["Profit"].sum() / df["Sales"].sum() * 100), 2),
    "avg_order_value": round(float(df["Sales"].sum() / df["Order ID"].nunique()), 2),
    "line_items": int(len(df)),
}
print(json.dumps(kpi, indent=2))

# %% [markdown]
# ## 6. Exploratory Data Analysis

# %%
# 6.1 Top 10 products by sales
top_products = (df.groupby("Product Name").agg(sales=("Sales", "sum"), profit=("Profit", "sum"), qty=("Quantity", "sum"))
                  .sort_values("sales", ascending=False).head(10).round(2))
print(top_products)
kpi["top10_products"] = [{"rank": i + 1, "product": p, "sales": float(r.sales)} for i, (p, r) in enumerate(top_products.iterrows())]

fig, ax = plt.subplots(figsize=(9, 5))
top_products["sales"].sort_values().plot.barh(ax=ax, color="#2563EB")
ax.set_title("Top 10 Products by Sales"); ax.set_xlabel("Sales ($)")
plt.tight_layout(); plt.savefig(IMG / "top10_products.png", dpi=130); plt.close()

# %%
# 6.2 Profitable categories / sub-categories
cat = df.groupby("Category").agg(sales=("Sales", "sum"), profit=("Profit", "sum"))
cat["margin_%"] = (cat["profit"] / cat["sales"] * 100).round(2)
print(cat.round(2))
sub = df.groupby("Sub-Category").agg(sales=("Sales", "sum"), profit=("Profit", "sum"))
sub["margin_%"] = (sub["profit"] / sub["sales"] * 100).round(2)
print(sub.sort_values("profit").round(2))
kpi["category"] = cat.round(2).reset_index().to_dict("records")
kpi["subcategory"] = sub.round(2).reset_index().to_dict("records")

fig, ax = plt.subplots(figsize=(9, 5))
sub["profit"].sort_values().plot.barh(ax=ax, color=["#DC2626" if v < 0 else "#059669" for v in sub["profit"].sort_values()])
ax.set_title("Profit by Sub-Category"); ax.set_xlabel("Profit ($)")
plt.tight_layout(); plt.savefig(IMG / "profit_by_subcategory.png", dpi=130); plt.close()

# %%
# 6.3 Monthly trend + MoM growth
monthly = df.groupby("Month Start").agg(sales=("Sales", "sum"), profit=("Profit", "sum"), orders=("Order ID", "nunique"))
monthly["mom_growth_%"] = (monthly["sales"].pct_change() * 100).round(2)
print(monthly.round(2).tail(12))
kpi["yearly"] = (df.groupby("Year").agg(sales=("Sales", "sum"), profit=("Profit", "sum"), orders=("Order ID", "nunique"))
                   .round(2).reset_index().to_dict("records"))
kpi["monthly_sales_first6"] = monthly["sales"].round(2).head(6).reset_index().astype({"Month Start": str}).to_dict("records")

fig, ax = plt.subplots(figsize=(11, 4.5))
ax.plot(monthly.index, monthly["sales"], color="#2563EB", lw=2, marker="o", ms=3)
ax.set_title("Monthly Sales Trend"); ax.set_ylabel("Sales ($)"); ax.grid(alpha=.3)
plt.tight_layout(); plt.savefig(IMG / "monthly_sales_trend.png", dpi=130); plt.close()

# %%
# 6.4 Regional performance
reg = df.groupby("Region").agg(sales=("Sales", "sum"), profit=("Profit", "sum"), orders=("Order ID", "nunique"))
reg["margin_%"] = (reg["profit"] / reg["sales"] * 100).round(2)
print(reg.sort_values("sales", ascending=False).round(2))
kpi["region"] = reg.round(2).reset_index().to_dict("records")

fig, ax = plt.subplots(figsize=(7, 4.5))
reg["sales"].sort_values().plot.barh(ax=ax, color="#7C3AED")
ax.set_title("Sales by Region"); ax.set_xlabel("Sales ($)")
plt.tight_layout(); plt.savefig(IMG / "sales_by_region.png", dpi=130); plt.close()

# %%
# 6.5 Discount impact on profit (important business insight)
bins = pd.cut(df["Discount"], [-0.01, 0, 0.10, 0.20, 0.30, 1.0], labels=["0%", "1-10%", "11-20%", "21-30%", ">30%"])
disc = df.groupby(bins, observed=True).agg(sales=("Sales", "sum"), profit=("Profit", "sum"), lines=("Row ID", "count"))
disc["margin_%"] = (disc["profit"] / disc["sales"] * 100).round(2)
print(disc.round(2))
kpi["discount_bands"] = disc.round(2).reset_index().rename(columns={"Discount": "band"}).astype({"band": str}).to_dict("records")

fig, ax = plt.subplots(figsize=(7, 4.5))
ax.bar(disc.index.astype(str), disc["margin_%"], color=["#059669" if v > 0 else "#DC2626" for v in disc["margin_%"]])
ax.axhline(0, color="black", lw=.8); ax.set_title("Profit Margin % by Discount Band"); ax.set_ylabel("Margin %")
plt.tight_layout(); plt.savefig(IMG / "discount_vs_margin.png", dpi=130); plt.close()

# %%
# 6.6 Segment & payment mode & profit-vs-sales scatter
seg = df.groupby("Segment").agg(sales=("Sales", "sum"), profit=("Profit", "sum"))
pay = df.groupby("Payment Mode").agg(sales=("Sales", "sum"), orders=("Order ID", "nunique"))
print(seg.round(2)); print(pay.round(2))
kpi["segment"] = seg.round(2).reset_index().to_dict("records")
kpi["payment_mode"] = pay.round(2).reset_index().to_dict("records")

sp = df.groupby("Product Name").agg(sales=("Sales", "sum"), profit=("Profit", "sum"))
fig, ax = plt.subplots(figsize=(8, 5))
ax.scatter(sp["sales"], sp["profit"], c=["#DC2626" if p < 0 else "#2563EB" for p in sp["profit"]], alpha=.8)
ax.axhline(0, color="black", lw=.8); ax.set_xlabel("Sales ($)"); ax.set_ylabel("Profit ($)"); ax.set_title("Profit vs Sales by Product")
plt.tight_layout(); plt.savefig(IMG / "profit_vs_sales.png", dpi=130); plt.close()
loss = sp[sp["profit"] < 0].sort_values("profit")
print("Loss-making products:", len(loss)); print(loss.round(2))
kpi["loss_products"] = loss.round(2).reset_index().to_dict("records")

# %%
# Save audit + KPI reference (acceptance criteria ke liye)
(ROOT / "docs").mkdir(exist_ok=True)
with open(ROOT / "docs" / "expected_kpis.json", "w") as f:
    json.dump({"audit_before_cleaning": audit, "cleaning_log": log, "kpis": kpi}, f, indent=2, default=str)
print("Done. Cleaned rows:", len(df))
