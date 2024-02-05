library(readr)
library(dplyr)
library(lubridate)
library(zoo)
library(writexl)
library(tidyr)
library(writexl)

# Reading the data
injuries_data <- read_csv('nba_OI.csv')
workforce_data <- read_csv('NBA_Workforce.csv')

# Identifying and excluding the IDs that haven't been QAed
unqaed_ids <- injuries_data %>% filter(is.na(`QA By`)) %>% pull(`ID Data`)
qaed_injuries_data <- injuries_data %>% filter(!(`ID Data` %in% unqaed_ids))


# Adding a 'Year' column to qaed_injuries_data for chronological ordering
qaed_injuries_data <- qaed_injuries_data %>%
mutate(Year = year(ymd_hms(`Incident Date`)))

injury_counts <- qaed_injuries_data %>%
  group_by(Year, `Business Period`, `Injury Status`) %>%
  summarise(Count = n(), .groups = 'drop') %>%
  pivot_wider(names_from = `Injury Status`, values_from = Count, values_fill = list(Count = 0))


# Merging workforce data with injury counts
merged_data <- left_join(injury_counts, workforce_data %>% select(Year, `Business Period`, `Number of Employees`), by = c("Year", "Business Period"))

# Calculating injury rates per 100 employees
merged_data <- merged_data %>%
  mutate(`Lost Time Rate` = (`Lost time` / `Number of Employees`) * 100,
         `No Lost Time Rate` = (`No lost time` / `Number of Employees`) * 100)

# Annualizing the numbers
days_in_year <- 365
days_in_period <- 30

merged_data <- merged_data %>%
  mutate(`Annualized Lost Time` = `Lost Time Rate` * (days_in_year / days_in_period),
         `Annualized No Lost Time` = `No Lost Time Rate` * (days_in_year / days_in_period))

# Calculate Moving Annual for every 12 periods
merged_data <- merged_data %>%
  arrange(Year, `Business Period`) %>%
  mutate(`MA Lost Time` = rollmean(`Annualized Lost Time`, 12, fill = NA, align = "right"),
         `MA No Lost Time` = rollmean(`Annualized No Lost Time`, 12, fill = NA, align = "right"))

# Export to Excel
output_path <- 'Rstudio_injury_analysis_output.xlsx'
write_xlsx(list(`Aggregated Data` = merged_data), output_path)

# Extract the IDs that haven't been QAed
unqaed_ids <- injuries_data %>% 
  filter(is.na(`QA By`)) %>% 
  pull(`ID Data`)

# View the unqaed IDs
print(unqaed_ids)