import pandas as pd

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

# Merging workforce data with injury counts
merged_data = pd.merge(injury_counts, workforce_data[['Year', 'Business Period', 'Number of Employees']], left_on=['Year', 'Business Period'], right_on=['Year', 'Business Period'])

# Calculating injury rates per 100 employees
merged_data['Lost Time Rate'] = (merged_data['Lost time'] / merged_data['Number of Employees']) * 100
merged_data['No Lost Time Rate'] = (merged_data['No lost time'] / merged_data['Number of Employees']) * 100

# Annualizing the numbers
days_in_year = 365  # For a standard year, need to account for
days_in_period = 30  # Assuming each period is 30 days, obv wrong and need to be fixed but can do it later on to put exactly how many days are in each period this is just and exmaple 

merged_data['Annualized Lost Time'] = merged_data['Lost Time Rate'] * (days_in_year / days_in_period)
merged_data['Annualized No Lost Time'] = merged_data['No Lost Time Rate'] * (days_in_year / days_in_period)

# Calculate Moving Annual for every 12 periods
merged_data['MA Lost Time'] = merged_data['Annualized Lost Time'].rolling(window=12, min_periods=1).mean()
merged_data['MA No Lost Time'] = merged_data['Annualized No Lost Time'].rolling(window=12, min_periods=1).mean()

# now make revised rates (lost time and no lost time), where the only difference is that emotional trauma is not included, under injury event type you check (acute emotional truama, priority one, and ??? (threat?)) 

# 

# Sorting data chronologically
merged_data = merged_data.sort_values(by=['Year', 'Business Period'])

# Export to Excel 
output_path = 'injury_analysis_output.xlsx'
merged_data.to_excel(output_path, index=False, sheet_name='Aggregated Data')

