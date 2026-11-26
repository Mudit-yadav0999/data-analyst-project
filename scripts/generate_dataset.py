"""
Generates a realistic Superstore-style retail dataset (synthetic, seeded) with
deliberately injected data-quality problems so the cleaning step is meaningful.

If you have the real Kaggle 'Sample - Superstore.csv', you can skip this script and
use that file instead (see README). 'Payment Mode' does not exist in the Kaggle file,
so the cleaning notebook adds it synthetically for that case.
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

# ---------------- Product catalogue ----------------
catalog = {
    ("Furniture", "Chairs"): [("Ergonomic Mesh Office Chair", 220), ("Executive Leather Chair", 380), ("Task Chair with Arms", 150), ("Conference Room Chair", 190)],
    ("Furniture", "Tables"): [("Oak Conference Table", 520), ("Adjustable Standing Desk", 410), ("Round Meeting Table", 330), ("Folding Training Table", 160)],
    ("Furniture", "Bookcases"): [("5-Shelf Wooden Bookcase", 210), ("Metal Display Bookcase", 175), ("Corner Bookcase Unit", 240)],
    ("Furniture", "Furnishings"): [("LED Desk Lamp", 45), ("Decorative Wall Clock", 38), ("Desk Organizer Set", 28), ("Floor Mat Anti-Fatigue", 55)],
    ("Office Supplies", "Binders"): [("Heavy Duty 3-Ring Binder", 14), ("Presentation Binder Pack", 22), ("Binder Index Dividers", 9)],
    ("Office Supplies", "Paper"): [("Premium Copy Paper Ream", 12), ("Recycled Printer Paper Box", 34), ("Colored Cardstock Pack", 18)],
    ("Office Supplies", "Storage"): [("Stackable File Storage Box", 40), ("Wire Mesh Organizer Rack", 65), ("Lockable File Cabinet", 180)],
    ("Office Supplies", "Art"): [("Professional Marker Set", 16), ("Sketch Pencil Collection", 11)],
    ("Office Supplies", "Appliances"): [("Compact Paper Shredder", 120), ("Desktop Air Purifier", 95), ("Electric Stapler Pro", 48)],
    ("Technology", "Phones"): [("Smartphone 128GB Black", 540), ("Business Phone Handset", 130), ("Wireless Headset Pro", 110), ("Smartphone Rugged Edition", 480)],
    ("Technology", "Accessories"): [("Wireless Ergonomic Mouse", 35), ("Mechanical Keyboard", 75), ("USB-C Docking Hub", 90), ("External SSD 1TB", 120)],
    ("Technology", "Copiers"): [("Laser Copier Workstation", 1650), ("Compact Desktop Copier", 780)],
    ("Technology", "Machines"): [("Label Printer Pro", 260), ("Thermal Receipt Printer", 190), ("Heavy Duty Laminator", 150)],
}
# profit characteristics per sub-category: (mean margin at 0% discount)
margin_base = {
    "Chairs": 0.22, "Tables": 0.06, "Bookcases": 0.10, "Furnishings": 0.30,
    "Binders": 0.40, "Paper": 0.42, "Storage": 0.15, "Art": 0.36, "Appliances": 0.28,
    "Phones": 0.20, "Accessories": 0.30, "Copiers": 0.38, "Machines": 0.08,
}

products = []
pid = 1
for (cat, sub), items in catalog.items():
    for name, price in items:
        prefix = {"Furniture": "FUR", "Office Supplies": "OFF", "Technology": "TEC"}[cat]
        products.append({"Product ID": f"{prefix}-{sub[:2].upper()}-{10000000 + pid}",
                         "Product Name": name, "Category": cat, "Sub-Category": sub, "List Price": price})
        pid += 1
products = pd.DataFrame(products)

# ---------------- Geography ----------------
geo = {
    "West": [("California", ["Los Angeles", "San Francisco", "San Diego"]), ("Washington", ["Seattle", "Spokane"]), ("Oregon", ["Portland"]), ("Arizona", ["Phoenix"])],
    "East": [("New York", ["New York City", "Buffalo"]), ("Pennsylvania", ["Philadelphia", "Pittsburgh"]), ("Massachusetts", ["Boston"]), ("Virginia", ["Richmond"])],
    "Central": [("Texas", ["Houston", "Dallas", "Austin"]), ("Illinois", ["Chicago"]), ("Michigan", ["Detroit"]), ("Minnesota", ["Minneapolis"])],
    "South": [("Florida", ["Miami", "Orlando"]), ("Georgia", ["Atlanta"]), ("North Carolina", ["Charlotte"]), ("Tennessee", ["Nashville"])],
}
region_weights = {"West": 0.32, "East": 0.28, "Central": 0.24, "South": 0.16}
region_margin_adj = {"West": 0.04, "East": 0.03, "Central": -0.06, "South": -0.01}

# ---------------- Customers ----------------
first = ["Aarav", "Emma", "Liam", "Olivia", "Noah", "Sophia", "Mason", "Ava", "Ethan", "Isabella", "Lucas", "Mia",
         "Logan", "Charlotte", "James", "Amelia", "Benjamin", "Harper", "Elijah", "Evelyn", "Priya", "Rahul", "Neha", "Arjun"]
last = ["Smith", "Johnson", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor", "Anderson", "Thomas", "Jackson",
        "White", "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson", "Clark", "Lewis", "Sharma", "Mehta", "Singh", "Patel"]
n_cust = 800
cust = pd.DataFrame({
    "Customer ID": [f"CU-{i:05d}" for i in range(1, n_cust + 1)],
    "Customer Name": [f"{rng.choice(first)} {rng.choice(last)}" for _ in range(n_cust)],
    "Segment": rng.choice(["Consumer", "Corporate", "Home Office"], n_cust, p=[0.52, 0.30, 0.18]),
})
# each customer has a home region/state/city (stable)
home = []
for _ in range(n_cust):
    reg = rng.choice(list(region_weights), p=list(region_weights.values()))
    state, cities = geo[reg][rng.integers(len(geo[reg]))]
    home.append((reg, state, rng.choice(cities)))
cust["Region"], cust["State"], cust["City"] = zip(*home)

# ---------------- Orders ----------------
start, end = pd.Timestamp("2022-01-01"), pd.Timestamp("2025-12-31")
days = pd.date_range(start, end)
# seasonality + growth
month_w = {1: .75, 2: .7, 3: .95, 4: .9, 5: 1.0, 6: 1.0, 7: .95, 8: 1.0, 9: 1.35, 10: 1.1, 11: 1.8, 12: 1.9}
w = np.array([month_w[d.month] * (1 + 0.18 * (d.year - 2022)) for d in days])
w /= w.sum()

rows = []
row_id = 1
order_no = 0
target = 9994
ship_modes = ["Standard Class", "Second Class", "First Class", "Same Day"]
pay_modes = ["Credit Card", "Debit Card", "UPI", "Net Banking", "Cash on Delivery", "PayPal"]
pay_p = [0.30, 0.20, 0.18, 0.10, 0.12, 0.10]
disc_vals = [0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50]
disc_p = [0.48, 0.06, 0.12, 0.05, 0.15, 0.07, 0.04, 0.03]

while row_id <= target:
    order_no += 1
    od = days[rng.choice(len(days), p=w)]
    c = cust.iloc[rng.integers(n_cust)]
    sm = rng.choice(ship_modes, p=[0.6, 0.19, 0.15, 0.06])
    lag = {"Standard Class": rng.integers(4, 8), "Second Class": rng.integers(2, 6), "First Class": rng.integers(1, 4), "Same Day": 0}[sm]
    pay = rng.choice(pay_modes, p=pay_p)
    oid = f"IN-{od.year}-{order_no:06d}"
    for _ in range(int(rng.choice([1, 2, 3, 4, 5], p=[0.35, 0.30, 0.18, 0.11, 0.06]))):
        if row_id > target:
            break
        p = products.iloc[rng.integers(len(products))]
        qty = int(rng.choice([1, 2, 3, 4, 5, 6, 7, 8], p=[0.22, 0.25, 0.20, 0.13, 0.10, 0.05, 0.03, 0.02]))
        disc = float(rng.choice(disc_vals, p=disc_p))
        price = p["List Price"] * rng.uniform(0.92, 1.08)
        sales = round(price * qty * (1 - disc), 2)
        margin = margin_base[p["Sub-Category"]] + region_margin_adj[c["Region"]] - 1.1 * disc + rng.normal(0, 0.05)
        profit = round(sales * margin, 2)
        rows.append([row_id, oid, od, od + pd.Timedelta(days=int(lag)), sm, c["Customer ID"], c["Customer Name"], c["Segment"],
                     "United States", c["City"], c["State"], c["Region"], p["Product ID"], p["Category"], p["Sub-Category"],
                     p["Product Name"], sales, qty, disc, profit, pay])
        row_id += 1

cols = ["Row ID", "Order ID", "Order Date", "Ship Date", "Ship Mode", "Customer ID", "Customer Name", "Segment", "Country",
        "City", "State", "Region", "Product ID", "Category", "Sub-Category", "Product Name", "Sales", "Quantity", "Discount",
        "Profit", "Payment Mode"]
df = pd.DataFrame(rows, columns=cols)

# ---------------- Inject data-quality problems (raw file is intentionally dirty) ----------------
df["Order Date"] = df["Order Date"].dt.strftime("%m/%d/%Y")
df["Ship Date"] = pd.to_datetime(df["Ship Date"]).dt.strftime("%m/%d/%Y")
df = df.astype({"Sales": "float64", "Discount": "float64"})

idx = lambda n: rng.choice(df.index, n, replace=False)

# 1) inconsistent category text
for i in idx(45): df.loc[i, "Category"] = df.loc[i, "Category"].upper()
for i in idx(45): df.loc[i, "Category"] = df.loc[i, "Category"].lower() + " "
for i in idx(30): df.loc[i, "Sub-Category"] = " " + df.loc[i, "Sub-Category"].lower()
for i in idx(25): df.loc[i, "Region"] = df.loc[i, "Region"].lower()
# 2) nulls
for col, n in [("Customer Name", 35), ("Segment", 30), ("Region", 20), ("Discount", 25), ("Payment Mode", 40), ("Profit", 8)]:
    df.loc[idx(n), col] = np.nan
# 3) negative / zero sales (data-entry errors)
for i in idx(14): df.loc[i, "Sales"] = -abs(df.loc[i, "Sales"])
for i in idx(4): df.loc[i, "Sales"] = 0.0
# 4) invalid dates
bad = ["13/45/2024", "N/A", "2024-99-01", "00/00/0000", "02/30/2023", "12/31/2031"]
for i, b in zip(idx(len(bad)), bad): df.loc[i, "Order Date"] = b
# 5) exact duplicate rows
dups = df.sample(60, random_state=7)
df = pd.concat([df, dups], ignore_index=True).sample(frac=1, random_state=3).reset_index(drop=True)

df.to_csv("data/raw/Superstore_raw.csv", index=False, encoding="latin-1")
print("raw rows:", len(df))
