import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Function to generate random dates within a specified range
def random_dates(start, end, n=10):
    start_u = int(start.timestamp())
    end_u = int(end.timestamp())
    return pd.to_datetime(np.random.randint(start_u, end_u, n), unit='s')

# Function to determine the business period based on the incident date
def determine_business_period(date, start_year):
    weeks_per_period = [4, 4, 5, 4, 4, 5, 4, 4, 5, 4, 4, 5]  # Weeks in each period
    year = start_year.year
    while date.year > year:
        year += 1
    period_start_date = datetime(year, 1, 1)
    for period, weeks in enumerate(weeks_per_period, start=1):
        period_end_date = period_start_date + timedelta(weeks=weeks)
        if period_start_date <= date < period_end_date:
            return period
        period_start_date = period_end_date
    return 12  # Default to last period if date is at the end of the year


# Complete list of NBA teams
nba_teams = [
    "Atlanta Hawks", "Boston Celtics", "Brooklyn Nets", "Charlotte Hornets", "Chicago Bulls",
    "Cleveland Cavaliers", "Dallas Mavericks", "Denver Nuggets", "Detroit Pistons", "Golden State Warriors",
    "Houston Rockets", "Indiana Pacers", "Los Angeles Clippers", "Los Angeles Lakers", "Memphis Grizzlies",
    "Miami Heat", "Milwaukee Bucks", "Minnesota Timberwolves", "New Orleans Pelicans", "New York Knicks",
    "Oklahoma City Thunder", "Orlando Magic", "Philadelphia 76ers", "Phoenix Suns", "Portland Trail Blazers",
    "Sacramento Kings", "San Antonio Spurs", "Toronto Raptors", "Utah Jazz", "Washington Wizards"
]

# Generating fake cost centres
cost_centres = [f"{chr(65+i)}{chr(65+j)}{str(random.randint(10, 99))}" for i in range(5) for j in range(4)]

num_rows = 15000
start_id = 2024000
start_date = datetime(2020, 1, 1)
end_date = datetime(2025, 12, 31)

# Creating the DataFrame
incident_dates = random_dates(start_date, end_date, num_rows)
business_periods = [determine_business_period(date, start_date) for date in incident_dates]


# Creating the DataFrame
df = pd.DataFrame({
    "ID Data": range(start_id, start_id + num_rows),
    "Incident Date": incident_dates,
    "Business Period": business_periods,
    "NBA Department": np.random.choice(nba_teams, num_rows),
    "Employee Cost Centre": np.random.choice(cost_centres, num_rows),
    "Primary Category": np.random.choice(['Employee Injury', 'Player Injury', 'Fan Injury'], num_rows, p=[0.8, 0.15, 0.05]),
    "NBA Location": np.random.choice(["Stadium A - City X", "Arena B - City Y", "Field C - City Z"], num_rows),
    "Injury Status": np.random.choice(['No lost time', 'Lost time'], num_rows, p=[0.8, 0.2]),
    "Injury Type": np.random.choice(['Emotional trauma', 'Sprain/strain', 'Non-specific injury', 'Other'], num_rows, p=[0.9, 0.02, 0.05, 0.03]),
    "Injury Event Type": np.random.choice(['Acute emotional event', 'Threat', 'Assault', 'Collision', 'Priority One'], num_rows, p=[0.8, 0.05, 0.05, 0.05, 0.05]),
    "Occupational?": np.random.choice([True, False], num_rows, p=[0.95, 0.05]),
    "Ergonomic?": np.random.choice([True, False], num_rows, p=[0.3, 0.7]),
    "Emotional Trauma?": np.random.choice([True, False], num_rows, p=[0.9, 0.1]),
    "Slip/Trip?": np.random.choice([True, False], num_rows, p=[0.10, 0.90]),
    "QA By": np.random.choice(['John Smith', 'Jane Doe', 'James Bond', None], num_rows, p=[0.33, 0.33, 0.33, 0.01])
})

# Sorting the DataFrame by date
df.sort_values("Incident Date", inplace=True)

# Saving to CSV
df.to_csv("nba_OI.csv", index=False)