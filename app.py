
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Sales Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- THEME ----------------
BG = "#0B1120"
CARD = "#131C2E"
BORDER = "#25334A"
TEXT = "#E8EEF8"
MUTED = "#8FA3BD"
BLUE = "#5B8CFF"
CYAN = "#42D6C5"
PURPLE = "#A78BFA"
ORANGE = "#F5A65B"

st.markdown("""
<style>
.stApp {
    background: #0B1120;
    color: #E8EEF8;
}
[data-testid="stHeader"] {
    background: #0B1120;
}
[data-testid="stSidebar"] {
    background: #10192A;
    border-right: 1px solid #25334A;
}
[data-testid="stSidebar"] * {
    color: #E8EEF8 !important;
}
.block-container {
    padding-top: 1.8rem;
    padding-bottom: 2rem;
    max-width: 1500px;
}
h1, h2, h3 {
    color: #E8EEF8 !important;
}
div[data-testid="stMetric"] {
    background: #131C2E;
    border: 1px solid #25334A;
    padding: 17px 18px;
    border-radius: 14px;
}
div[data-testid="stMetricLabel"] {
    color: #8FA3BD !important;
}
div[data-testid="stMetricValue"] {
    color: #E8EEF8 !important;
    font-size: 26px !important;
}
div[data-testid="stMetricDelta"] {
    font-size: 12px;
}
div[data-testid="stPlotlyChart"] {
    background: #131C2E;
    border: 1px solid #25334A;
    border-radius: 14px;
    padding: 8px;
}
div[data-testid="stDataFrame"] {
    border: 1px solid #25334A;
    border-radius: 12px;
}
hr {
    border-color: #25334A;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    file_path = Path("data/cleaned/sales_cleaned.csv")
    df = pd.read_csv(file_path)

    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")

    for col in ["Sales", "Profit", "Quantity", "Discount"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df

df = load_data()

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## 📊 Sales Analytics")
st.sidebar.caption("Superstore Business Intelligence")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔎 Filters")

regions = sorted(df["Region"].dropna().unique())
categories = sorted(df["Category"].dropna().unique())
segments = sorted(df["Segment"].dropna().unique())

selected_regions = st.sidebar.multiselect(
    "Region",
    regions,
    default=regions
)

selected_categories = st.sidebar.multiselect(
    "Category",
    categories,
    default=categories
)

selected_segments = st.sidebar.multiselect(
    "Customer Segment",
    segments,
    default=segments
)

min_date = df["Order Date"].min().date()
max_date = df["Order Date"].max().date()

date_range = st.sidebar.date_input(
    "Order Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# ---------------- FILTER DATA ----------------
filtered = df[
    df["Region"].isin(selected_regions) &
    df["Category"].isin(selected_categories) &
    df["Segment"].isin(selected_segments)
].copy()

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    filtered = filtered[
        (filtered["Order Date"].dt.date >= date_range[0]) &
        (filtered["Order Date"].dt.date <= date_range[1])
    ]

if filtered.empty:
    st.warning("No data found for the selected filters.")
    st.stop()

# ---------------- KPIs ----------------
total_sales = filtered["Sales"].sum()
total_profit = filtered["Profit"].sum()
total_orders = filtered["Order ID"].nunique()
total_quantity = filtered["Quantity"].sum()

profit_margin = (total_profit / total_sales * 100) if total_sales else 0
avg_order_value = total_sales / total_orders if total_orders else 0

# ---------------- HEADER ----------------
st.markdown("# 📈 Sales Performance")
st.markdown(
    "<p style='color:#8FA3BD;'>Business overview · Revenue · Profitability · Customer insights</p>",
    unsafe_allow_html=True
)

st.markdown("---")

# ---------------- KPI CARDS ----------------
c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("💰 Total Revenue", f"${total_sales:,.0f}")
c2.metric("📈 Net Profit", f"${total_profit:,.0f}")
c3.metric("🛒 Total Orders", f"{total_orders:,}")
c4.metric("🎯 Profit Margin", f"{profit_margin:.2f}%")
c5.metric("📦 Units Sold", f"{total_quantity:,}")

st.markdown("")

# ---------------- CHART THEME ----------------
chart_layout = dict(
    template="plotly_dark",
    paper_bgcolor=CARD,
    plot_bgcolor=CARD,
    font=dict(color=TEXT, family="Arial"),
    margin=dict(l=35, r=20, t=50, b=35),
    xaxis=dict(
        gridcolor=BORDER,
        zerolinecolor=BORDER
    ),
    yaxis=dict(
        gridcolor=BORDER,
        zerolinecolor=BORDER
    ),
    legend=dict(
        bgcolor="rgba(0,0,0,0)"
    )
)

# ---------------- MONTHLY SALES ----------------
monthly = (
    filtered.groupby(filtered["Order Date"].dt.to_period("M"))["Sales"]
    .sum()
    .reset_index()
)
monthly["Month"] = monthly["Order Date"].astype(str)
monthly = monthly.sort_values("Month")

# ---------------- ROW 1 CHARTS ----------------
left, right = st.columns([1.65, 1])

with left:
    st.markdown("### Revenue Trend")

    fig = px.area(
        monthly,
        x="Month",
        y="Sales",
        markers=True
    )

    fig.update_traces(
        line_color=BLUE,
        line_width=3,
        fillcolor="rgba(91,140,255,0.16)",
        marker=dict(size=5)
    )

    fig.update_layout(
        **chart_layout,
        height=370,
        xaxis_title="Month",
        yaxis_title="Revenue"
    )

    st.plotly_chart(fig, use_container_width=True)

with right:
    st.markdown("### Sales by Category")

    category_sales = (
        filtered.groupby("Category")["Sales"]
        .sum()
        .reset_index()
        .sort_values("Sales", ascending=True)
    )

    fig = px.bar(
        category_sales,
        x="Sales",
        y="Category",
        orientation="h",
        text_auto=".2s"
    )

    fig.update_traces(
        marker_color=CYAN,
        textposition="outside"
    )

    fig.update_layout(
        **chart_layout,
        height=370,
        xaxis_title="Revenue",
        yaxis_title=""
    )

    st.plotly_chart(fig, use_container_width=True)

# ---------------- ROW 2 CHARTS ----------------
left, right = st.columns(2)

with left:
    st.markdown("### Regional Profit")

    region_profit = (
        filtered.groupby("Region")["Profit"]
        .sum()
        .reset_index()
        .sort_values("Profit")
    )

    fig = px.bar(
        region_profit,
        x="Region",
        y="Profit",
        color="Profit",
        color_continuous_scale=["#F26B75", "#5F85DC", "#42D6C5"]
    )

    fig.update_layout(
        **chart_layout,
        height=350,
        showlegend=False,
        coloraxis_showscale=False,
        xaxis_title="Region",
        yaxis_title="Profit"
    )

    st.plotly_chart(fig, use_container_width=True)

with right:
    st.markdown("### Top 10 Products")

    top_products = (
        filtered.groupby("Product Name")["Sales"]
        .sum()
        .nlargest(10)
        .reset_index()
        .sort_values("Sales")
    )

    fig = px.bar(
        top_products,
        x="Sales",
        y="Product Name",
        orientation="h"
    )

    fig.update_traces(
        marker_color=PURPLE
    )

    fig.update_layout(
        **chart_layout,
        height=350,
        xaxis_title="Revenue",
        yaxis_title=""
    )

    st.plotly_chart(fig, use_container_width=True)

# ---------------- DISCOUNT ANALYSIS ----------------
st.markdown("### Discount vs Profit Analysis")

fig = px.scatter(
    filtered,
    x="Discount",
    y="Profit",
    color="Category",
    size="Sales",
    hover_data=["Product Name", "Region", "Sales"],
    opacity=0.65
)

fig.update_layout(
    **chart_layout,
    height=420,
    xaxis_title="Discount",
    yaxis_title="Profit"
)

st.plotly_chart(fig, use_container_width=True)

# ---------------- SUMMARY ----------------
st.markdown("---")
st.markdown("### 📋 Filtered Sales Data")

st.caption(f"{len(filtered):,} records found")

st.dataframe(
    filtered,
    use_container_width=True,
    height=350,
    hide_index=True
)

csv = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇️ Download Filtered Data",
    data=csv,
    file_name="filtered_sales.csv",
    mime="text/csv"
)

st.markdown(
    "<p style='text-align:center;color:#8FA3BD;'>Sales Analytics Dashboard · Python · Streamlit · Plotly</p>",
    unsafe_allow_html=True
)
