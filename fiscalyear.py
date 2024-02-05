from datetime import datetime, timedelta

class Fiscal445Calendar:
    def __init__(self, start_year):
        self.start_year = start_year
        self.periods = self._generate_periods()

    def _generate_periods(self):
        periods = []
        current_date = datetime(self.start_year, 1, 1)
        
        for period in range(1, 13):
            if period % 3 == 0:
                # 5-week month
                end_date = current_date + timedelta(weeks=5) - timedelta(days=1)
            else:
                # 4-week month
                end_date = current_date + timedelta(weeks=4) - timedelta(days=1)
            
            periods.append((current_date, end_date))
            current_date = end_date + timedelta(days=1)
        
        # Adjust for the last period to end on Dec 31st
        periods[-1] = (periods[-1][0], datetime(self.start_year, 12, 31))
        
        return periods

    def get_period(self, period_number):
        if 1 <= period_number <= 12:
            return self.periods[period_number - 1]
        else:
            raise ValueError("Period number must be between 1 and 12.")
    
    def display_periods(self):
        for i, period in enumerate(self.periods, 1):
            print(f"P{i}: {period[0].strftime('%m/%d/%Y')} - {period[1].strftime('%m/%d/%Y')}")

# Usage
fiscal_calendar = Fiscal445Calendar(2022)
fiscal_calendar.display_periods()
