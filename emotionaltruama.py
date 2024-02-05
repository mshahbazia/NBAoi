import pandas as pd
from openpyxl import load_workbook

# Define a function to calculate rates and annualize
def calculate_rates_and_annualize(data, num_employees_col, days_in_year=365, days_in_period=30):
    data = data.copy()  # Ensure we are not modifying the original dataframe
    data['Lost Time Rate'] = (data['Lost time'] / data[num_employees_col]) * 100
    data['No Lost Time Rate'] = (data['No lost time'] / data[num_employees_col]) * 100

    data['Annualized Lost Time'] = data['Lost Time Rate'] * (days_in_year / days_in_period)
    data['Annualized No Lost Time'] = data['No Lost Time Rate'] * (days_in_year / days_in_period)

    data['MA Lost Time'] = data['Annualized Lost Time'].rolling(window=12, min_periods=1).mean()
    data['MA No Lost Time'] = data['Annualized No Lost Time'].rolling(window=12, min_periods=1).mean()

    return data

# Load the data
injuries_path = 'nba_OI.csv'
workforce_path = 'NBA_Workforce.csv'
injuries_data = pd.read_csv(injuries_path)
workforce_data = pd.read_csv(workforce_path)

# Identifying and excluding the IDs that haven't been QAed
unqaed_ids = injuries_data[injuries_data['QA By'].isna()]['ID Data']
qaed_injuries_data = injuries_data[~injuries_data['ID Data'].isin(unqaed_ids)].copy()

# Adding a 'Year' column to qaed_injuries_data for chronological ordering
qaed_injuries_data['Year'] = pd.to_datetime(qaed_injuries_data['Incident Date']).dt.year

# Filter based on Emotional Trauma status
emotional_trauma_true = qaed_injuries_data[qaed_injuries_data["Emotional Trauma?"]].copy()
emotional_trauma_false = qaed_injuries_data[~qaed_injuries_data["Emotional Trauma?"]].copy()

# Define conditions for specific injury event types
conditions = {
    'Acute Emotional Events': qaed_injuries_data['Injury Event Type'].isin(['Acute emotional event', 'Priority One']),
    'Ergonomic?': qaed_injuries_data['Ergonomic?'],
    'Slip/Trip?': qaed_injuries_data['Slip/Trip?'],
    'Collision': qaed_injuries_data['Injury Event Type'] == 'collision'
}

# Initialize a DataFrame to store specific injury type data
specific_injury_data = pd.DataFrame()

# Process data based on conditions and calculate counts for each condition
for condition_name, condition in conditions.items():
    # Calculate sum of condition within each group
    condition_sum = qaed_injuries_data[condition].groupby([qaed_injuries_data['Year'], qaed_injuries_data['Business Period']]).size().reset_index(name=condition_name)
    # Merge the condition sums with the specific injury data
    specific_injury_data = pd.merge(specific_injury_data, condition_sum, how='outer', on=['Year', 'Business Period'])

# Calculate Moving Annual for each condition in specific injury data
for condition_name in conditions.keys():
    specific_injury_data[f'MA {condition_name}'] = specific_injury_data[condition_name].rolling(window=12, min_periods=1).mean()

# Perform calculations for all injuries and emotional trauma statuses
all_injuries_processed = calculate_rates_and_annualize(qaed_injuries_data, 'Number of Employees')
emotional_trauma_true_processed = calculate_rates_and_annualize(emotional_trauma_true, 'Number of Employees')
emotional_trauma_false_processed = calculate_rates_and_annualize(emotional_trauma_false, 'Number of Employees')

# Sorting data chronologically
all_injuries_processed = all_injuries_processed.sort_values(by=['Year', 'Business Period'])
emotional_trauma_true_processed = emotional_trauma_true_processed.sort_values(by=['Year', 'Business Period'])
emotional_trauma_false_processed = emotional_trauma_false_processed.sort_values(by=['Year', 'Business Period'])
specific_injury_data = specific_injury_data.sort_values(by=['Year', 'Business Period'])

# Export to Excel to different sheets within the same file
output_path = 'injury_analysis_output.xlsx'
with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    all_injuries_processed.to_excel(writer, index=False, sheet_name='All Injuries')
    emotional_trauma_true_processed.to_excel(writer, index=False, sheet_name='Emotional Trauma True')
    emotional_trauma_false_processed.to_excel(writer, index=False, sheet_name='Emotional Trauma False')
    specific_injury_data.to_excel(writer, index=False, sheet_name='Specific Injury Data')
