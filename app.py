import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio

# =========================
# 🎨 THEME SETUP
# =========================
st.set_page_config(
    page_title="Retail Analytics Dashboard",
    layout="wide",
    page_icon="📊"
)

pio.templates.default = "plotly_dark"

st.title("📊 Retail Sales Analytics Dashboard")

# =========================
# 📂 LOAD DATA (NO EXTRA PREPROCESSING NEEDED)
# =========================
@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_data.csv", encoding='latin-1')
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    return df

df = load_data()

# =========================
# 🎛 SIDEBAR FILTERS (STABLE VERSION)
# =========================
st.sidebar.header("🔍 Filters")

# Country filter
countries = st.sidebar.multiselect(
    "🌍 Country",
    df['Country'].unique(),
    default=df['Country'].unique()
)

# Date filter (SAFE)
min_date = df['InvoiceDate'].min()
max_date = df['InvoiceDate'].max()

start_date = st.sidebar.date_input("📅 Start Date", min_date.date())
end_date = st.sidebar.date_input("📅 End Date", max_date.date())

# APPLY FILTERS
df = df[df['Country'].isin(countries)]
df = df[(df['InvoiceDate'].dt.date >= start_date) &
        (df['InvoiceDate'].dt.date <= end_date)]

# =========================
# ⚡ QUICK INSIGHTS BUTTONS (FIXED VERSION)
# =========================
st.sidebar.markdown("### ⚡ Quick Filters")

if st.sidebar.button("📈 Last 7 Days"):
    df = df[df['InvoiceDate'] >= df['InvoiceDate'].max() - pd.Timedelta(days=7)]

if st.sidebar.button("📅 This Month"):
    df = df[df['Month'] == df['Month'].max()]

if st.sidebar.button("🌍 Top Countries"):
    top_countries = df['Country'].value_counts().head(3).index
    df = df[df['Country'].isin(top_countries)]

# =========================
# 📌 KPI CARDS
# =========================
col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Revenue", f"{df['Revenue'].sum():,.0f}")
col2.metric("🧾 Orders", df['InvoiceNo'].nunique())
col3.metric("👥 Customers", df['CustomerID'].nunique())
col4.metric("📦 Products", df['Description'].nunique())

st.markdown("---")

# =========================
# 📈 MONTHLY TREND (UPGRADED)
# =========================
st.subheader("📈 Monthly Revenue Trend")

monthly = df.groupby('Month', as_index=False)['Revenue'].sum()
monthly['RollingAvg'] = monthly['Revenue'].rolling(3).mean()

fig = px.line(
    monthly,
    x='Month',
    y=['Revenue', 'RollingAvg'],
    markers=True,
    title="Revenue vs Rolling Average"
)

fig.update_traces(line=dict(width=3))
st.plotly_chart(fig, use_container_width=True)

# =========================
# 📊 CUMULATIVE TREND
# =========================
st.subheader("📊 Cumulative Revenue Growth")

monthly['CumulativeRevenue'] = monthly['Revenue'].cumsum()

fig = px.area(
    monthly,
    x='Month',
    y='CumulativeRevenue',
    title="Cumulative Revenue Growth"
)

st.plotly_chart(fig, use_container_width=True)

# =========================
# 🔥 SEASONAL HEATMAP (ADVANCED)
# =========================
st.subheader("🔥 Sales Heatmap (Hour vs Weekday)")

heatmap = df.pivot_table(
    values='Revenue',
    index='Hour',
    columns='DayName',
    aggfunc='sum'
)

fig = px.imshow(
    heatmap,
    aspect="auto",
    color_continuous_scale="Blues",
    title="Revenue Intensity"
)

st.plotly_chart(fig, use_container_width=True)

# =========================
# 🌍 COUNTRY ANALYSIS
# =========================
st.subheader("🌍 Top Countries by Revenue")

country_sales = df.groupby('Country', as_index=False)['Revenue'].sum()
country_sales = country_sales.sort_values('Revenue', ascending=False).head(10)

fig = px.bar(
    country_sales,
    x='Country',
    y='Revenue',
    text_auto=True
)

st.plotly_chart(fig, use_container_width=True)

# =========================
# 📦 TOP PRODUCTS
# =========================
st.subheader("📦 Top Products")

top_products = df.groupby('Description', as_index=False)['Revenue'].sum()
top_products = top_products.sort_values('Revenue', ascending=False).head(10)

fig = px.bar(
    top_products,
    x='Revenue',
    y='Description',
    orientation='h',
    text_auto=True
)

st.plotly_chart(fig, use_container_width=True)

# =========================
# ⏰ HOURLY TREND
# =========================
st.subheader("⏰ Hourly Sales Pattern")

hourly = df.groupby('Hour', as_index=False)['Revenue'].sum()

fig = px.line(hourly, x='Hour', y='Revenue', markers=True)
st.plotly_chart(fig, use_container_width=True)

# =========================
# 👥 TOP CUSTOMERS
# =========================
st.subheader("👥 Top Customers")

top_customers = df.groupby('CustomerID', as_index=False)['Revenue'].sum()
top_customers = top_customers.sort_values('Revenue', ascending=False).head(10)

fig = px.bar(top_customers, x='CustomerID', y='Revenue', text_auto=True)
st.plotly_chart(fig, use_container_width=True)

# =========================
# 📊 CUSTOMER DISTRIBUTION
# =========================
st.subheader("📊 Customer Spending Distribution")

customer_spending = df.groupby('CustomerID', as_index=False)['Revenue'].sum()

fig = px.histogram(customer_spending, x='Revenue', nbins=50)
st.plotly_chart(fig, use_container_width=True)

# =========================
# 📅 WEEKDAY ANALYSIS
# =========================
st.subheader("📅 Sales by Weekday")

weekday_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

weekday = df.groupby('DayName', as_index=False)['Revenue'].sum()
weekday['DayName'] = pd.Categorical(weekday['DayName'], categories=weekday_order, ordered=True)
weekday = weekday.sort_values('DayName')

fig = px.bar(weekday, x='DayName', y='Revenue', text_auto=True)

st.plotly_chart(fig, use_container_width=True)

#Run Steamlit command
#python -m streamlit run app.py
