import pandas as pd
import matplotlib.pyplot as plt
from openpyxl import load_workbook
from openpyxl.drawing.image import Image
from openpyxl.utils.dataframe import dataframe_to_rows
from io import BytesIO

# Load the Excel file
file_path = 'injury_analysis_output.xlsx'  # Replace with the path to your Excel file
df = pd.read_excel(file_path)

# Perform calculations
last_ma_lost_time = df['MA Lost Time'].iloc[-1]
last_year_ma_lost_time = df['MA Lost Time'].iloc[-13]
last_ma_no_lost_time = df['MA No Lost Time'].iloc[-1]
last_year_ma_no_lost_time = df['MA No Lost Time'].iloc[-13]

# Prepare data for comparison
comparison_data = {
    'Category': ['MA Lost Time', 'MA No Lost Time'],
    'Last Year Value': [last_year_ma_lost_time, last_year_ma_no_lost_time],
    'Current Year Value': [last_ma_lost_time, last_ma_no_lost_time],
    'Difference': [last_ma_lost_time - last_year_ma_lost_time, last_ma_no_lost_time - last_year_ma_no_lost_time]
}

comparison_df = pd.DataFrame(comparison_data)

# Create a bar chart
fig, ax = plt.subplots(figsize=(8, 6))
categories = comparison_df['Category']
index = range(len(categories))
bar_width = 0.35
ax.bar(index, comparison_df['Last Year Value'], bar_width, label='Last Year')
ax.bar([i + bar_width for i in index], comparison_df['Current Year Value'], bar_width, label='Current Year')
ax.set_xlabel('Category')
ax.set_ylabel('Values')
ax.set_title('Comparison of MA Lost Time and MA No Lost Time')
ax.set_xticks([i + bar_width / 2 for i in index])
ax.set_xticklabels(categories)
ax.legend()


# Save the bar chart as an image in a BytesIO object
bar_chart_image = BytesIO()
plt.savefig(bar_chart_image, format='png')
bar_chart_image.seek(0)

# Averaging 'Lost Time rate' values for each quarter over the last 5 years
rows_per_year = 4 * 3  # 4 quarters per year, 3 periods per quarter
rows_for_5_years = rows_per_year * 5
last_5_years_data = df['Lost Time Rate'].tail(rows_for_5_years)

quarterly_averages = last_5_years_data.groupby(df.tail(rows_for_5_years).index // 3).mean()
x_labels = [f'{year} Q{quarter}' for year in range(df['Year'].iloc[-rows_for_5_years], df['Year'].iloc[-1] + 1) for quarter in range(1, 5)]

# Adjusting the number of x_labels to match the length of the quarterly_averages
x_labels = x_labels[:len(quarterly_averages)]

# Create the line chart
plt.figure(figsize=(15, 6))
plt.plot(x_labels, quarterly_averages, marker='o')
plt.xlabel('Year and Quarter')
plt.ylabel('Lost Time Injuries per 100 Employees')
plt.title('Lost Time Injury Rate Over the Last 5 Years')
plt.xticks(rotation=45)
plt.grid(True)

# Save the line chart as an image in a BytesIO object
line_chart_image = BytesIO()
plt.savefig(line_chart_image, format='png')
line_chart_image.seek(0)

# Load the original Excel file and target the "Aggregated Data" sheet
wb = load_workbook(file_path)
agg_data_ws = wb["Aggregated Data"]

# Append the bar chart data to the "Aggregated Data" sheet
for r in dataframe_to_rows(comparison_df, index=False, header=True):
    agg_data_ws.append(r)

# Add the bar chart image to the "Aggregated Data" sheet
bar_chart_img = Image(bar_chart_image)
agg_data_ws.add_image(bar_chart_img, 'S3')  # Adjust the cell location as needed

# Add the line chart image to the same sheet
line_chart_img = Image(line_chart_image)
agg_data_ws.add_image(line_chart_img, 'S25')  # Adjust the cell location as needed


# Save the updated workbook
updated_excel_path = 'injury_analysis_output.xlsx'   # Replace with the desired path
wb.save(updated_excel_path)
