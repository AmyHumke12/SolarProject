# To run streamlit you must type streamlit run app.py in the terminal.
# To clear the current run and refresh with new visuals press CTRL + C to stop the already running app
import streamlit as st
import pandas as pd
import pickle
import requests
import io
import numpy as np
import matplotlib.pyplot as plt
import calendar
from datetime import datetime

# Define GitHub raw file URL
github_url = "https://raw.githubusercontent.com/AmyHumke12/SolarProject/main/bi_solar_dashboard_final.pkl"

# Load the pickle file from GitHub
@st.cache_data
def load_data():
    response = requests.get(github_url)
    if response.status_code == 200:
        return pickle.load(io.BytesIO(response.content))
    else:
        st.error(f"❌ Failed to load bi_solar_dashboard_final.pkl. HTTP Status: {response.status_code}")
        return None

# Load data
df = load_data()

if df is not None:
    st.title("Solar Production Dashboard")
    
    # Convert date column
    df['date_timestamp'] = pd.to_datetime(df['date_timestamp'])

    # Aggregation Level Selector (Year, Quarter, Month)
    period_option = st.sidebar.selectbox(
        "Select Aggregation Level",
        ["Year", "Quarter", "Month"],
        index=2  # Default to "Month"
    )

    # Date Range Slider
    min_date = df['date_timestamp'].min().date()
    max_date = df['date_timestamp'].max().date()
    today_date = datetime.today().date()

    date_range = st.sidebar.slider(
        "Select Date Range",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, today_date)
    )

    # Apply date filter and create a copy
    df_filtered = df[(df['date_timestamp'].dt.date >= date_range[0]) & 
                     (df['date_timestamp'].dt.date <= date_range[1])].copy()

    # Custom Fiscal Quarter Mapping
    def get_fiscal_quarter(month):
        if month in [5, 6, 7]:  # May, June, July
            return "Q1"
        elif month in [8, 9, 10]:  # August, September, October
            return "Q2"
        elif month in [11, 12, 1]:  # November, December, January
            return "Q3"
        else:  # February, March, April
            return "Q4"

    # Aggregation Based on Period Selection
    if period_option == "Year":
        df_filtered = df_filtered.groupby("Billing_Year").agg({
            "Production": "sum",
            "Consumption": "sum",
            "COST": "sum",
            "Unified_Net_Usage": "sum",
            "Unified_Production": "sum",
            "Unified_Consumption": "sum"
        }).reset_index()
        x_col = "Billing_Year"

    elif period_option == "Quarter":
        df_filtered["Fiscal_Quarter"] = df_filtered["date_timestamp"].dt.month.apply(get_fiscal_quarter)
        df_filtered = df_filtered.groupby(["Billing_Year", "Fiscal_Quarter"]).agg({
            "Production": "sum",
            "Consumption": "sum",
            "COST": "sum",
            "Unified_Net_Usage": "sum",
            "Unified_Production": "sum",
            "Unified_Consumption": "sum"
        }).reset_index()
        df_filtered["Quarter_Label"] = df_filtered["Billing_Year"].astype(str) + " " + df_filtered["Fiscal_Quarter"]
        x_col = "Quarter_Label"

    else:  # Month
        df_filtered["YearMonth"] = df_filtered["date_timestamp"].dt.to_period("M")
        df_filtered = df_filtered.groupby("YearMonth").agg({
            "Production": "sum",
            "Consumption": "sum",
            "COST": "sum",
            "Unified_Net_Usage": "sum",
            "Unified_Production": "sum",
            "Unified_Consumption": "sum"
        }).reset_index()
        x_col = "YearMonth"

    ################################    LINE CHART ########################################################
    # ✅ Solar Production vs. Consumption (Line Chart with Labels)
    st.write(f"### {period_option}-Aggregated Solar Production vs. Consumption")
    fig, ax = plt.subplots(figsize=(10, 5))

    # Plot the lines
    ax.plot(df_filtered[x_col].astype(str), df_filtered['Production'], label='Solar Production (kWh)', color='green')
    ax.plot(df_filtered[x_col].astype(str), df_filtered['Consumption'], label='Consumption (kWh)', color='blue', linestyle="--")

    # Add labels to Production line
    for i, txt in enumerate(df_filtered['Production']):
        ax.text(i, txt, f'{int(txt)}', ha='center', va='bottom' if txt > 0 else 'top', fontsize=8, color='green')

    # Add labels to Consumption line
    for i, txt in enumerate(df_filtered['Consumption']):
        ax.text(i, txt, f'{int(txt)}', ha='center', va='bottom' if txt > 0 else 'top', fontsize=8, color='blue')

    ax.set_xlabel(period_option)
    ax.set_ylabel("kWh")
    ax.legend()
    ax.grid(True)
    plt.xticks(rotation=45)
    st.pyplot(fig)

################################    STACKED BAR CHART ########################################################
# ✅ Add Labels to Stacked Bar Chart
st.write(f"### {period_option}-Aggregated Net Usage, Production, and Consumption")
x = np.arange(len(df_filtered))
bar_width = 0.35

fig2, ax2 = plt.subplots(figsize=(12, 6))
bottom_values = np.minimum(df_filtered['Unified_Production'], df_filtered['Unified_Consumption'])
top_values = np.maximum(df_filtered['Unified_Production'], df_filtered['Unified_Consumption']) - bottom_values
bottom_label = df_filtered['Unified_Production'] <= df_filtered['Unified_Consumption']

bars1 = ax2.bar(x - bar_width, df_filtered['Unified_Net_Usage'], width=bar_width, label='Net Usage', color='limegreen')
bars2 = ax2.bar(x, bottom_values, width=bar_width, color=np.where(bottom_label, 'orange', 'darkblue'), label='Production')
bars3 = ax2.bar(x, top_values, bottom=bottom_values, width=bar_width, color=np.where(bottom_label, 'darkblue', 'orange'), label='Consumption')

# Add data labels for Net Usage
for bar in bars1:
    height = bar.get_height()
    if height != 0:
        ax2.text(bar.get_x() + bar.get_width() / 2, height + 2, f'{int(height)}', ha='center', va='bottom')

# Add data labels for stacked bars
for bar2, bar3 in zip(bars2, bars3):
    production_height = bar2.get_height()
    usage_height = bar3.get_height() + production_height

    # Bottom label
    if production_height != 0:
        ax2.text(bar2.get_x() + bar2.get_width() / 2, production_height / 2, f'{int(production_height)}', ha='center', va='center', color='white')

    # Top label
    if usage_height != 0:
        ax2.text(bar3.get_x() + bar3.get_width() / 2, usage_height + 2, f'{int(usage_height)}', ha='center', va='bottom')

ax2.set_xlabel(period_option)
ax2.set_ylabel("kWh")
ax2.legend(['Net Usage', 'Production', 'Consumption'])
plt.xticks(rotation=45)
st.pyplot(fig2)

