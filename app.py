import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="Nassau Candy Profitability Dashboard",
    page_icon="🍫",
    layout="wide"
)

st.markdown("""
<style>

/* Main Background */
.stApp {
    background-color: #FFF8F0;
}

/* Headers */
h1, h2, h3 {
    color: #5D4037;
}

/* KPI Cards */
[data-testid="stMetric"] {
    background-color: #F5E6D3;
    border: 1px solid #D7CCC8;
    padding: 15px;
    border-radius: 12px;
    text-align: center;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #F5E6D3;
}

/* Tabs */
button[data-baseweb="tab"] {
    font-size: 16px;
    font-weight: 600;
}

/* Info Boxes */
div[data-baseweb="notification"] {
    border-radius: 10px;
}

/* Tables */
[data-testid="stDataFrame"] {
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

st.title("🍫 Product Line Profitability & Margin Performance Analysis")
st.markdown("### Nassau Candy Distributor")

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------

df = pd.read_csv("Nassau Candy Distributor.csv")

# ---------------------------------------------------
# DATA PREPARATION
# ---------------------------------------------------

df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=True)
df["Ship Date"] = pd.to_datetime(df["Ship Date"], dayfirst=True)

df["Gross_Margin_%"] = (
    (df["Gross Profit"] / df["Sales"]) * 100
).round(2)

df["Profit Per Unit"] = (
    df["Gross Profit"] / df["Units"]
).round(2)

df["Month"] = df["Order Date"].dt.month_name()
df["Year"] = df["Order Date"].dt.year

# ---------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------

st.sidebar.header("🔍 Dashboard Filters")

start_date = st.sidebar.date_input(
    "Start Date",
    value=df["Order Date"].min()
)

end_date = st.sidebar.date_input(
    "End Date",
    value=df["Order Date"].max()
)

selected_divisions = st.sidebar.multiselect(
    "Division",
    options=sorted(df["Division"].dropna().unique()),
    default=sorted(df["Division"].dropna().unique())
)

selected_region = st.sidebar.multiselect(
    "Region",
    options=sorted(df["Region"].dropna().unique()),
    default=sorted(df["Region"].dropna().unique())
)

selected_country = st.sidebar.multiselect(
    "Country/Region",
    options=sorted(df["Country/Region"].dropna().unique()),
    default=sorted(df["Country/Region"].dropna().unique())
)

selected_state = st.sidebar.multiselect(
    "State/Province",
    options=sorted(df["State/Province"].dropna().unique()),
    default=sorted(df["State/Province"].dropna().unique())
)

product_search = st.sidebar.text_input(
    "Search Product"
)

margin_threshold = st.sidebar.slider(
    "Minimum Margin %",
    min_value=0,
    max_value=100,
    value=0
)

# ---------------------------------------------------
# FILTER DATA
# ---------------------------------------------------

filtered_df = df[
    (df["Order Date"] >= pd.to_datetime(start_date)) &
    (df["Order Date"] <= pd.to_datetime(end_date))
]

filtered_df = filtered_df[
    filtered_df["Division"].isin(selected_divisions)
]

filtered_df = filtered_df[
    filtered_df["Region"].isin(selected_region)
]

filtered_df = filtered_df[
    filtered_df["Country/Region"].isin(selected_country)
]

filtered_df = filtered_df[
    filtered_df["State/Province"].isin(selected_state)
]

if product_search:
    filtered_df = filtered_df[
        filtered_df["Product Name"]
        .str.contains(product_search, case=False, na=False)
    ]

# Margin Threshold Filter
filtered_df = filtered_df[
    filtered_df["Gross_Margin_%"] >= margin_threshold
]

# Create Cost Column
filtered_df = filtered_df.copy()

filtered_df["Cost"] = (
    filtered_df["Sales"] - filtered_df["Gross Profit"]
)


# ---------------------------------------------------
# KPI CARDS
# ---------------------------------------------------

total_revenue = filtered_df["Sales"].sum()

total_profit = filtered_df["Gross Profit"].sum()

avg_margin = filtered_df["Gross_Margin_%"].mean()

avg_profit_per_unit = filtered_df["Profit Per Unit"].mean()

monthly_margin = (filtered_df.groupby(filtered_df["Order Date"].dt.to_period("M"))["Gross_Margin_%"].mean().reset_index())

margin_volatility = monthly_margin["Gross_Margin_%"].std()

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "💰 Total Revenue",
        f"${total_revenue:,.0f}"
    )

with col2:
    st.metric(
        "📈 Total Gross Profit",
        f"${total_profit:,.0f}"
    )

with col3:
    st.metric(
        "🎯 Avg Gross Margin %",
        f"{avg_margin:.2f}%"
    )

with col4:
    st.metric(
        "📦 Profit Per Unit",
        f"${avg_profit_per_unit:.2f}"
    )

with col5:
    st.metric(
        "📈 Margin Volatility",
        f"{margin_volatility:.2f}%"
    )

st.divider()

# ---------------------------------------------------
# EXECUTIVE SUMMARY
# ---------------------------------------------------

st.subheader("📌 Executive Summary")

if not filtered_df.empty:
    top_product = (
        filtered_df.groupby("Product Name")["Gross Profit"]
        .sum()
        .idxmax()
    )
else:
    top_product = "N/A"

st.info(
    f"""
    • Total Revenue Generated: ${total_revenue:,.0f}

    • Total Gross Profit: ${total_profit:,.0f}

    • Average Gross Margin: {avg_margin:.2f}%

    • Most Profitable Product: {top_product}

    • Dashboard helps identify high-margin products,
      revenue concentration, cost risks, and profitability trends.
    """
)

# ---------------------------------------------------
# DASHBOARD TABS
# ---------------------------------------------------

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "📈 Product Profitability",
        "🏢 Division Performance",
        "💰 Cost Diagnostics",
        "🎯 Profit Concentration",
        "📅 Time Analysis"
    ]
)

# ===================================================
# TAB 1 : PRODUCT PROFITABILITY
# ===================================================

with tab1:

    st.subheader("📈 Product Profitability Overview")

    product_summary = (
        filtered_df
        .groupby("Product Name")
        .agg({
            "Sales": "sum",
            "Gross Profit": "sum",
            "Gross_Margin_%": "mean"
        })
        .reset_index()
    )

    # -----------------------------
    # PRODUCT MARGIN LEADERBOARD
    # -----------------------------

    st.markdown("### 🏆 Product Margin Leaderboard")

    top_margin = (
        product_summary
        .sort_values("Gross_Margin_%", ascending=False)
        .head(10)
    )

    fig_margin = px.bar(
        top_margin,
        x="Gross_Margin_%",
        y="Product Name",
        orientation="h",
        title="Top 10 Products by Gross Margin %",
        color="Gross_Margin_%"
    )

    st.plotly_chart(fig_margin, use_container_width=True)

    st.info(""" Several products consistently achieve higher gross margins, indicating strong profitability and pricing effectiveness. """)

    # -----------------------------
    # PROFIT CONTRIBUTION
    # -----------------------------

    st.markdown("### 💰 Profit Contribution by Product")

    top_profit = (
        product_summary
        .sort_values("Gross Profit", ascending=False)
        .head(10)
    )

    fig_profit = px.bar(
        top_profit,
        x="Product Name",
        y="Gross Profit",
        title="Top 10 Products by Gross Profit",
        color="Gross Profit"
    )

    st.plotly_chart(fig_profit, use_container_width=True)

    st.info(""" Insight: A small group of products contributes a significant portion of total gross profit, making them key profit drivers. """)

    # -----------------------------
    # PRODUCT PROFITABILITY TABLE
    # -----------------------------

    st.markdown("### 📋 Product Profitability Table")

    st.dataframe(
        product_summary.sort_values(
            "Gross Profit",
            ascending=False
        ),
        use_container_width=True
    )

# ===================================================
# TAB 2 : DIVISION PERFORMANCE
# ===================================================

with tab2:

    st.subheader("🏢 Division Performance Dashboard")

    division_summary = (
        filtered_df
        .groupby("Division")
        .agg({
            "Sales": "sum",
            "Gross Profit": "sum",
            "Gross_Margin_%": "mean"
        })
        .reset_index()
    )

    # -----------------------------
    # REVENUE VS PROFIT COMPARISON
    # -----------------------------

    st.markdown("### 💰 Revenue vs Profit Comparison")

    fig_revenue_profit = px.bar(
        division_summary,
        x="Division",
        y=["Sales", "Gross Profit"],
        barmode="group",
        title="Revenue vs Gross Profit by Division"
    )

    st.plotly_chart(
        fig_revenue_profit,
        use_container_width=True
    )

    st.info(""" Insight: Comparing revenue and gross profit helps identify divisions that generate strong sales while maintaining healthy profitability. """)

    # -----------------------------
    # MARGIN DISTRIBUTION
    # -----------------------------

    st.markdown("### 🎯 Margin Distribution by Division")

    fig_margin_dist = px.box(
        filtered_df,
        x="Division",
        y="Gross_Margin_%",
        color="Division",
        title="Gross Margin Distribution Across Divisions"
    )

    st.plotly_chart(
        fig_margin_dist,
        use_container_width=True
    )

    st.info(""" Insight: Divisions with wider margin variation may experience inconsistent profitability and should be monitored closely. """)

    # -----------------------------
    # DIVISION PERFORMANCE TABLE
    # -----------------------------

    st.markdown("### 📋 Division Performance Table")

    st.dataframe(
        division_summary.sort_values(
            "Gross Profit",
            ascending=False
        ),
        use_container_width=True
    )


# ===================================================
# TAB 3 : COST DIAGNOSTICS
# ===================================================

with tab3:

    st.subheader("💰 Cost vs Margin Diagnostics")

    # -----------------------------
    # COST VS SALES SCATTER PLOT
    # -----------------------------

    st.markdown("### 📊 Cost vs Sales Scatter Plot")

    fig_scatter = px.scatter(
        filtered_df,
        x="Cost",
        y="Sales",
        size="Gross Profit",
        color="Gross_Margin_%",
        hover_name="Product Name",
        title="Cost vs Sales Analysis"
    )

    st.plotly_chart(
        fig_scatter,
        use_container_width=True
    )

    st.info(""" Insight: Products with high sales but relatively high costs may offer opportunities for cost reduction and margin improvement. """)

    # -----------------------------
    # MARGIN RISK FLAGS
    # -----------------------------

    st.markdown("### 🚨 Margin Risk Flags")

    risk_products = (
        filtered_df[
            filtered_df["Gross_Margin_%"] < 60
        ]
        .groupby("Product Name")
        .agg({
            "Sales":"sum",
            "Cost":"sum",
            "Gross Profit":"sum",
            "Gross_Margin_%":"mean"
        })
        .reset_index()
        .round(2)
        .sort_values(
            "Gross_Margin_%",
            ascending=True
        )
    )

    if len(risk_products) > 0:

        st.warning(
            f"{len(risk_products)} products have Gross Margin below 60%."
        )

    else:

        st.success(
            "No low-margin products found."
        )

    st.info(""" Insight: Low-margin products should be reviewed for pricing, supplier costs, or promotional effectiveness to improve profitability. """)

    # -----------------------------
    # COST DIAGNOSTICS TABLE
    # -----------------------------

    st.markdown("### 📋 Cost Diagnostics Table")

    st.dataframe(
        risk_products,
        use_container_width=True
    )

# ===================================================
# TAB 4 : PROFIT CONCENTRATION ANALYSIS
# ===================================================

with tab4:

    st.subheader("🎯 Profit Concentration Analysis")

    product_summary = (
        filtered_df
        .groupby("Product Name")
        .agg({
            "Sales":"sum",
            "Gross Profit":"sum",
            "Gross_Margin_%":"mean"
        })
        .reset_index()
    )

    # ----------------------------------
    # REVENUE PARETO ANALYSIS
    # ----------------------------------

    st.markdown("### 💰 Revenue Pareto Chart")

    revenue_pareto = product_summary.sort_values(
        by="Sales",
        ascending=False
    )

    revenue_pareto["Revenue_%"] = (
        revenue_pareto["Sales"] /
        revenue_pareto["Sales"].sum()
    ) * 100

    revenue_pareto["Cumulative_Revenue_%"] = (
        revenue_pareto["Revenue_%"].cumsum()
    )

    fig = go.Figure()

    fig.add_bar(
        x=revenue_pareto["Product Name"],
        y=revenue_pareto["Revenue_%"],
        name="Revenue %"
    )

    fig.add_scatter(
        x=revenue_pareto["Product Name"],
        y=revenue_pareto["Cumulative_Revenue_%"],
        mode="lines+markers",
        name="Cumulative Revenue %"
    )

    fig.add_hline(
        y=80,
        line_dash="dash"
    )

    fig.update_layout(
        title="Pareto Analysis - Revenue",
        xaxis_title="Product",
        yaxis_title="Contribution (%)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.info(""" Insight: A limited number of products generate the majority of total revenue, indicating revenue concentration within the product portfolio. """)

    # ----------------------------------
    # PROFIT PARETO ANALYSIS
    # ----------------------------------

    st.markdown("### 📈 Profit Pareto Chart")

    profit_pareto = product_summary.sort_values(
        by="Gross Profit",
        ascending=False
    )

    profit_pareto["Profit_%"] = (
        profit_pareto["Gross Profit"] /
        profit_pareto["Gross Profit"].sum()
    ) * 100

    profit_pareto["Cumulative_Profit_%"] = (
        profit_pareto["Profit_%"].cumsum()
    )

    fig2 = go.Figure()

    fig2.add_bar(
        x=profit_pareto["Product Name"],
        y=profit_pareto["Profit_%"],
        name="Profit %"
    )

    fig2.add_scatter(
        x=profit_pareto["Product Name"],
        y=profit_pareto["Cumulative_Profit_%"],
        mode="lines+markers",
        name="Cumulative Profit %"
    )

    fig2.add_hline(
        y=80,
        line_dash="dash"
    )

    fig2.update_layout(
        title="Pareto Analysis - Profit",
        xaxis_title="Product",
        yaxis_title="Contribution (%)"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    st.info(""" Insight: Profit contribution is concentrated among a small group of products, making these products critical to overall business performance. """)

    # ----------------------------------
    # DEPENDENCY INDICATORS
    # ----------------------------------

    st.markdown("### ⚠️ Dependency Indicators")

    top3_revenue = round(
        revenue_pareto["Revenue_%"]
        .head(3)
        .sum(),
        2
    )

    top3_profit = round(
        profit_pareto["Profit_%"]
        .head(3)
        .sum(),
        2
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Top 3 Products Revenue Contribution",
            f"{top3_revenue:.2f}%"
        )

    with col2:
        st.metric(
            "Top 3 Products Profit Contribution",
            f"{top3_profit:.2f}%"
        )

    # Full-width callout
    st.warning(f"""
    ⚠️ Product Concentration Risk

    The top 3 products contribute {top3_revenue:.1f}% of total revenue and
    {top3_profit:.1f}% of total profit.

    This concentration is driven primarily by the Wonka Bar product line,
    which dominates both sales and profitability.

    Heavy dependence on a small number of products increases business risk.
    Any decline in demand, supply chain disruption, or competitive pressure
    could significantly impact overall financial performance.

    Recommendation: Diversify revenue sources by growing additional profitable
    product lines and reducing reliance on a limited set of products.
    """)

    # ----------------------------------
    # CONCENTRATION SUMMARY
    # ----------------------------------

    st.markdown("### 📋 Profit Concentration Table")

    concentration_table = revenue_pareto[
        [
            "Product Name",
            "Sales",
            "Revenue_%",
            "Cumulative_Revenue_%"
        ]
    ].round(2)

    st.dataframe(
        concentration_table,
        use_container_width=True
    )

# ===================================================
# TAB 5 : TIME ANALYSIS
# ===================================================

with tab5:

    st.subheader("📅 Time Analysis")

    # ----------------------------------
    # Monthly Revenue Trend
    # ----------------------------------

    st.markdown("### 📈 Monthly Revenue Trend")

    monthly_sales = (
        filtered_df
        .groupby("Month")
        .agg({"Sales":"sum"})
        .reset_index()
    )

    month_order = [
        "January","February","March","April",
        "May","June","July","August",
        "September","October","November","December"
    ]

    monthly_sales["Month"] = pd.Categorical(
        monthly_sales["Month"],
        categories=month_order,
        ordered=True
    )

    monthly_sales = monthly_sales.sort_values("Month")

    fig = px.line(
        monthly_sales,
        x="Month",
        y="Sales",
        markers=True,
        title="Monthly Revenue Trend"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.info(""" Insight: Revenue trends help identify seasonal demand patterns and periods of strong business performance throughout the year. """)

    # ----------------------------------
    # Monthly Profit Trend
    # ----------------------------------

    st.markdown("### 💰 Monthly Profit Trend")

    monthly_profit = (
        filtered_df
        .groupby("Month")
        .agg({"Gross Profit":"sum"})
        .reset_index()
    )

    monthly_profit["Month"] = pd.Categorical(
        monthly_profit["Month"],
        categories=month_order,
        ordered=True
    )

    monthly_profit = monthly_profit.sort_values("Month")

    fig = px.line(
        monthly_profit,
        x="Month",
        y="Gross Profit",
        markers=True,
        title="Monthly Gross Profit Trend"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.info(""" Insight: Monitoring profit trends alongside revenue ensures that business growth is supported by sustainable profitability. """)

    # ----------------------------------
    # Monthly Margin Trend
    # ----------------------------------

    st.markdown("### 🎯 Monthly Margin Trend")

    monthly_margin = (
        filtered_df
        .groupby("Month")
        .agg({"Gross_Margin_%":"mean"})
        .reset_index()
    )

    monthly_margin["Month"] = pd.Categorical(
        monthly_margin["Month"],
        categories=month_order,
        ordered=True
    )

    monthly_margin = monthly_margin.sort_values("Month")

    fig = px.line(
        monthly_margin,
        x="Month",
        y="Gross_Margin_%",
        markers=True,
        title="Monthly Gross Margin Trend"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.info(""" Insight: Stable gross margins indicate effective pricing and cost management, while fluctuations may signal changing business conditions. """)

    # ----------------------------------
    # Yearly Performance
    # ----------------------------------

    st.markdown("### 📊 Yearly Performance")

    yearly_summary = (
        filtered_df
        .groupby("Year")
        .agg({
            "Sales":"sum",
            "Gross Profit":"sum"
        })
        .reset_index()
    )

    fig = px.bar(
        yearly_summary,
        x="Year",
        y=["Sales","Gross Profit"],
        barmode="group",
        title="Yearly Revenue vs Profit"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.info(""" Insight: Year-over-year performance comparison helps evaluate long-term revenue growth and profitability trends. """)

    # ----------------------------------
    # Time Analysis Table
    # ----------------------------------

    st.markdown("### 📋 Monthly Summary Table")

    time_table = (
        filtered_df
        .groupby("Month")
        .agg({
            "Sales":"sum",
            "Gross Profit":"sum",
            "Gross_Margin_%":"mean"
        })
        .reset_index()
    )

    time_table["Month"] = pd.Categorical(
        time_table["Month"],
        categories=month_order,
        ordered=True
    )

    time_table = time_table.sort_values("Month")

    st.dataframe(
        time_table,
        use_container_width=True
    )

# ---------------------------------------------------
# BUSINESS RECOMMENDATIONS
# ---------------------------------------------------

st.divider()

st.subheader("📌 Business Recommendations")

st.success("""
1. Prioritize marketing and inventory planning for high-profit products.

2. Review low-margin products to identify pricing and cost optimization opportunities.

3. Reduce dependence on a small number of revenue-driving products.

4. Expand successful high-margin product categories.

5. Monitor margin trends and volatility to maintain sustainable profitability.
""")



# cd "C:\Users\arjan\OneDrive\Desktop\Streamlit"
# streamlit run app.py