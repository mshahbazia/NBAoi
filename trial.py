import pandas as pd
from openpyxl import load_workbook

# Load the data
injuries_path = 'nba_OI.csv'
workforce_path = 'NBA_Workforce.csv'
injuries_data = pd.read_csv(injuries_path)
workforce_data = pd.read_csv(workforce_path)

# Identifying and excluding the IDs that haven't been QAed
unqaed_ids = injuries_data[injuries_data['QA By'].isna()]['ID Data']
qaed_injuries_data = injuries_data[~injuries_data['ID Data'].isin(unqaed_ids)]
qaed_injuries_data = qaed_injuries_data.copy()

# Adding a 'Year' column to qaed_injuries_data for chronological ordering
qaed_injuries_data['Year'] = pd.to_datetime(qaed_injuries_data['Incident Date']).dt.year

# Counting 'Lost Time' and 'No Lost Time' injury statuses for each period
injury_counts = qaed_injuries_data.groupby(['Year', 'Business Period', 'Injury Status']).size().unstack(fill_value=0).reset_index()

# Define conditions for specific injury event types
conditions = {
    'Acute Emotional Events': qaed_injuries_data['Injury Event Type'].isin(['Acute emotional event', 'Priority One']),
    'Ergonomic?': qaed_injuries_data['Ergonomic?'] == True,
    'Slip/Trip?': qaed_injuries_data['Slip/Trip?'] == True,
    'Collision': qaed_injuries_data['Injury Event Type'] == 'collision'
}

# Initialize a DataFrame to store specific injury type data
specific_injury_data = injury_counts[['Year', 'Business Period']].copy()

grouped_data = qaed_injuries_data.groupby(['Year', 'Business Period'])

# Calculating counts for specific injury types within each group and merging with injury_counts
for condition_name, condition in conditions.items():
    # Calculate sum of condition within each group
    condition_sum = condition.groupby([qaed_injuries_data['Year'], qaed_injuries_data['Business Period']]).sum().reset_index(name=condition_name)
    
    # Merge the condition sums with injury_counts
    injury_counts = pd.merge(injury_counts, condition_sum, how='left', on=['Year', 'Business Period'])
    
    # Store the sum and Calculate Moving Annual for each condition in specific_injury_data
    specific_injury_data[condition_name] = condition_sum[condition_name]
    specific_injury_data[f'MA {condition_name}'] = injury_counts[condition_name].rolling(window=12, min_periods=1).mean()

# Merging workforce data with injury counts
merged_data = pd.merge(injury_counts, workforce_data[['Year', 'Business Period', 'Number of Employees']], left_on=['Year', 'Business Period'], right_on=['Year', 'Business Period'])


# Remove specific injury type columns from merged_data before exporting
merged_data = merged_data.drop(columns=list(conditions.keys()))
def calculate_rates_and_annualize(data, num_employees_col, days_in_year=365, days_in_period=30):
    data['Lost Time Rate'] = (data['Lost time'] / data[num_employees_col]) * 100
    data['No Lost Time Rate'] = (data['No lost time'] / data[num_employees_col]) * 100

    data['Annualized Lost Time'] = data['Lost Time Rate'] * (days_in_year / days_in_period)
    data['Annualized No Lost Time'] = data['No Lost Time Rate'] * (days_in_year / days_in_period)

    data['MA Lost Time'] = data['Annualized Lost Time'].rolling(window=12, min_periods=1).mean()
    data['MA No Lost Time'] = data['Annualized No Lost Time'].rolling(window=12, min_periods=1).mean()

    return data


# Apply calculations to the original data
merged_data = calculate_rates_and_annualize(merged_data, 'Number of Employees')

# Filter out rows where "Emotional Trauma?" is "True" and apply the same calculations
filtered_data = merged_data[merged_data["Emotional Trauma?"].str.upper() != "TRUE"].copy()

filtered_data = calculate_rates_and_annualize(filtered_data, 'Number of Employees')

# Sorting data chronologically
merged_data = merged_data.sort_values(by=['Year', 'Business Period'])
specific_injury_data = specific_injury_data.sort_values(by=['Year', 'Business Period'])
filtered_data = filtered_data.sort_values(by=['Year', 'Business Period'])

# Export to Excel to different sheets within the same file
output_path = 'injury_analysis_output.xlsx'
with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    merged_data.to_excel(writer, index=False, sheet_name='Aggregated Data')
    specific_injury_data.to_excel(writer, index=False, sheet_name='Specific Injury Data')
    filtered_data.to_excel(writer, index=False, sheet_name='Filtered Aggregated Data')

