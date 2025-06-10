import pandas as pd

# --- 1. Load and Clean Data ---
try:
    df = pd.read_csv('Sensex25years.csv')
except FileNotFoundError:
    print("Error: 'Sensex25years.csv' not found.")
    exit()

# Drop unnecessary columns
df = df.drop(['Open', 'High', 'Low', 'Vol.'], axis=1)

# Clean and convert data types
df['Price'] = df['Price'].str.replace(',', '').astype(float)
df['Change %'] = df['Change %'].str.replace('%', '', regex=False)
df['Change %'] = pd.to_numeric(df['Change %'], errors='coerce')

# Correctly parse the date and handle potential errors
# Use format='%d-%m-%Y' to match your data, then sort for correct calculations
df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y', errors='coerce')
df.dropna(subset=['Date'], inplace=True)
df = df.sort_values('Date').reset_index(drop=True)

# Create 'Year' column after sorting
df['Year'] = df['Date'].dt.year

# --- 2. Calculate Metrics ---
# Calculate 'Delta' (day-over-day % change) using the sorted data
# pct_change() is more efficient for this task
df['Delta'] = (df['Price'].pct_change() * 100).round(2)
# Calculate 'Gamma' (difference between reported change and calculated Delta)
df['Gamma'] = (df['Change %'] - df['Delta']).round(2)
display (df)

# --- 3. Perform Annual Analysis ---
# Group by 'Year' and aggregate the counts for each condition based on the 'Delta' column
yearly_summary = df.groupby('Year').agg(
    days_lt_minus_1=pd.NamedAgg(column='Delta', aggfunc=lambda x: ((x <= -1) & (x >= -2)).sum()),
    days_between_minus_2_and_10=pd.NamedAgg(column='Delta', aggfunc=lambda x: ((x < -2) & (x >= -10)).sum())
).reset_index()

# Rename columns for clarity
yearly_summary.columns = [
    'Year',
    'Days with Change < -2%',
    'Days with Change in [-10%, -2%]'
]

# Display the final summary table
print("Annual Summary of Negative Change Days (based on calculated Delta):")
print(yearly_summary)
