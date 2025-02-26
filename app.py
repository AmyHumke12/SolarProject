# To run streamlit you must type streamlit run app.py in the terminal.
# To clear the current run and refresh with new visuals press CTRL + C to stop the already running app
import streamlit as st
st.set_page_config(layout="wide")
import pandas as pd
import pickle
import requests
import io
import numpy as np
import matplotlib.pyplot as plt
import calendar
from datetime import datetime
from datetime import datetime, timedelta


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
    
# ✅ Production & Consumption (Lines) + Net Usage (Bars) on the Same Axis
st.write(f"### {period_option}-Aggregated Solar Production, Consumption, and Net Usage")

fig, ax = plt.subplots(figsize=(10, 5))

# ✅ Plot Net Usage as a bar chart (Transparent for visibility)
ax.bar(df_filtered[x_col].astype(str), df_filtered['Unified_Net_Usage'], 
       label='Net Usage (kWh)', color='#8B0000', alpha=0.5, zorder=1)

# ✅ Plot Solar Production as a line
ax.plot(df_filtered[x_col].astype(str), df_filtered['Production'], 
        label='Solar Production (kWh)', color='#228B22', marker='o', zorder=2)

# ✅ Plot Consumption as a line
ax.plot(df_filtered[x_col].astype(str), df_filtered['Consumption'], 
        label='Consumption (kWh)', color='#1E90FF', linestyle="--", marker='o', zorder=2)

# ✅ Ensure the axis is centered on zero for all elements
ax.axhline(y=0, color='black', linestyle='--', linewidth=1, zorder=0)

# ✅ Axis Labels and Legends
ax.set_xlabel(period_option)
ax.set_ylabel("Energy (kWh)")
ax.legend(loc="upper left")

ax.grid(True, linestyle='--', alpha=0.6)
plt.xticks(rotation=45)

st.pyplot(fig)





################################    COST BAR CHART ########################################################

# Define required columns for the cost bar chart
cost_columns = ['Billing_Year', 'Billing_Month', 'Row_Level_Savings', 
                'Row_Level_Payout', 'Cumulative_Realized_Savings', 'Remaining_Balance']

# 🔹 STEP 1: Apply User-Selected Date Filters
df_filtered_cost = df[
    (df['date_timestamp'].dt.date >= date_range[0]) &
    (df['date_timestamp'].dt.date <= date_range[1])
].copy()

# 🔹 STEP 2: Ensure `df_filtered_cost` Exists Even If Empty
if df_filtered_cost.empty:
    st.warning("⚠️ No cost data available for the selected date range.")
    df_filtered_cost = pd.DataFrame(columns=cost_columns)  # Define an empty DataFrame with correct columns

# Define a custom order for Billing Months (May - April)
month_order = ["May", "June", "July", "August", "September",
               "October", "November", "December", "January", "February", "March", "April"]

# Assign a numeric ordering for billing months based on the fiscal cycle
df_filtered_cost['Month_Order'] = df_filtered_cost['Billing_Month'].apply(lambda x: month_order.index(x))

# 🔹 STEP 3: Monthly Aggregation (BASE DATA)
def filter_savings_or_payout(group):
    if (group['Row_Level_Savings'] > 0).any() and (group['Row_Level_Payout'] > 0).any():
        # Keep the one with the highest total in that month
        if group['Row_Level_Savings'].sum() > group['Row_Level_Payout'].sum():
            group['Row_Level_Payout'] = 0  # Remove Payout
        else:
            group['Row_Level_Savings'] = 0  # Remove Savings
    return group

df_monthly = df_filtered_cost.groupby(['Billing_Year', 'Billing_Month', 'Month_Order']).agg({
    'Row_Level_Savings': 'sum',
    'Row_Level_Payout': 'sum',
    'Cumulative_Realized_Savings': 'max',
    'Remaining_Balance': 'min'
}).reset_index()

# ✅ Apply the fix to remove cases where both exist in a single month
df_monthly = df_monthly.groupby(['Billing_Year', 'Billing_Month']).apply(filter_savings_or_payout).reset_index(drop=True)

# Sort by Billing Year first, then by Month Order
df_monthly = df_monthly.sort_values(by=['Billing_Year', 'Month_Order']).drop(columns=['Month_Order'])

# Create a new column for x-axis labeling using Billing_Year and Billing_Month
df_monthly['YearMonth'] = df_monthly.apply(lambda row: f"{row['Billing_Year']} {row['Billing_Month']}", axis=1)

# 🔹 STEP 4: Aggregate from the Correct Monthly Data
if period_option == "Year":
    df_aggregated = df_monthly.groupby(["Billing_Year"]).agg({
        'Row_Level_Savings': 'sum',
        'Row_Level_Payout': 'sum',
        'Cumulative_Realized_Savings': 'max',  # Highest cumulative savings in the year
        'Remaining_Balance': 'min'  # Lowest remaining balance
    }).reset_index()

    x_col = "Billing_Year"

elif period_option == "Quarter":
    # Map Billing_Month to Fiscal Quarter
    def get_fiscal_quarter(month):
        if month in ["May", "June", "July"]:
            return "Q1"
        elif month in ["August", "September", "October"]:
            return "Q2"
        elif month in ["November", "December", "January"]:
            return "Q3"
        else:
            return "Q4"

    df_monthly["Fiscal_Quarter"] = df_monthly["Billing_Month"].apply(get_fiscal_quarter)

    df_aggregated = df_monthly.groupby(["Billing_Year", "Fiscal_Quarter"]).agg({
        'Row_Level_Savings': 'sum',
        'Row_Level_Payout': 'sum',
        'Cumulative_Realized_Savings': 'max',  # Highest cumulative savings in the quarter
        'Remaining_Balance': 'min'  # Lowest balance during the quarter
    }).reset_index()

    df_aggregated["Quarter_Label"] = df_aggregated["Billing_Year"].astype(str) + " " + df_aggregated["Fiscal_Quarter"]
    x_col = "Quarter_Label"

else:  # Default to Monthly View
    df_aggregated = df_monthly
    x_col = "YearMonth"

# 🔹 STEP 5: Create the bar chart
st.write(f"### {period_option}-Aggregated Realized Savings and Payout Uncovered")

fig, ax = plt.subplots(figsize=(14, 6))
bar_width = 0.4
x = range(len(df_aggregated))

# Plot Realized Savings
bars1 = ax.bar(x, df_aggregated['Row_Level_Savings'], width=bar_width, label='Realized Savings', color='#228B22')

# Plot Payout Uncovered
bars2 = ax.bar([i + bar_width for i in x], df_aggregated['Row_Level_Payout'], width=bar_width, label='Billed Amount', color='#8B0000')

# Add labels to bars
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, height + 2, f'${int(height)}',
                    ha='center', va='bottom', fontsize=8)

# Customize the chart
ax.set_xlabel(period_option, fontsize=12)
ax.set_ylabel('Amount ($)', fontsize=12)
ax.set_title(f'{period_option}-Aggregated Realized Savings and Billed Amount', fontsize=16)

# ✅ Fix x-axis label formatting for better readability
ax.set_xticks(range(len(df_aggregated)))
ax.set_xticklabels(df_aggregated[x_col], rotation=45, ha='right', fontsize=10)

plt.legend(fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()

st.pyplot(fig)


################################    BREAK EVEN CHART ########################################################
# Add a dynamic heading
st.write("### Has the System Recovered Its Cost?")

# Use df directly for Break-Even analysis
df_break_even = df[['date_timestamp', 'Actual_Remaining_Balance', 'Estimated_Remaining_Balance', 'Data_Type_Label']].copy()
df_break_even['date'] = df_break_even['date_timestamp'].dt.date

# Get Yesterday's Date
yesterday = datetime.now().date() - timedelta(days=1)

# Get last available balance before yesterday
data_up_to_yesterday = df_break_even[df_break_even['date'] <= yesterday]

if not data_up_to_yesterday.empty:
    last_row = data_up_to_yesterday.iloc[-1]
    current_remaining_balance = last_row['Actual_Remaining_Balance']
    current_date = last_row['date']
    
    # Only show the actual remaining balance
    st.write(f"**As of {current_date}, the remaining balance is ${current_remaining_balance:.2f}.**")
else:
    st.write("No data available up to yesterday.")

# Identify break-even points
break_even_actual = df_break_even[df_break_even['Actual_Remaining_Balance'] <= 0]
break_even_estimated = df_break_even[(df_break_even['Data_Type_Label'] == 'Estimated') & (df_break_even['Estimated_Remaining_Balance'] <= 0)]

break_even_actual_date = break_even_actual.iloc[0]['date'] if not break_even_actual.empty else None
break_even_estimated_date = break_even_estimated.iloc[0]['date'] if not break_even_estimated.empty else None

if break_even_actual_date:
    st.write(f"**Break-even for Actual Remaining Balance: {break_even_actual_date}**")
else:
    st.write("The Actual Remaining Balance does not reach zero within the available data.")

if break_even_estimated_date:
    st.write(f"**Break-even for Estimated Remaining Balance: {break_even_estimated_date}**")
else:
    st.write("The Estimated Remaining Balance does not reach zero within the available data.")

# Plot Actual and Estimated Remaining Balances
fig, ax = plt.subplots(figsize=(12, 6))

# Plot Actual Remaining Balance
ax.plot(df_break_even['date'], df_break_even['Actual_Remaining_Balance'], label='Actual Remaining Balance', color='#1E90FF')

# Plot Estimated Remaining Balance
estimated_data = df_break_even[df_break_even['Data_Type_Label'] == 'Estimated']
if not estimated_data.empty:
    ax.plot(estimated_data['date'], estimated_data['Estimated_Remaining_Balance'], label='Estimated Remaining Balance', color='#228B22')

# Add the break-even lines
if break_even_actual_date:
    ax.axvline(x=break_even_actual_date, color='#1E90FF', linestyle='--', label=f'Actual Break-Even: {break_even_actual_date}')

if break_even_estimated_date:
    ax.axvline(x=break_even_estimated_date, color='#228B22', linestyle='--', label=f'Estimated Break-Even: {break_even_estimated_date}')

# Add a horizontal line for zero balance
ax.axhline(y=0, color='red', linestyle='--', label='Break-Even Point')

# Configure the plot
ax.set_xlabel('Date')
ax.set_ylabel('Remaining Balance ($)')
ax.set_title('Remaining Balance Over Time')
ax.legend(loc='upper right')
ax.grid(True)
plt.tight_layout()

st.pyplot(fig)
