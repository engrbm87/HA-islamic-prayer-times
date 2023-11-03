from hijri_converter import convert
from datetime import datetime

# Get the current Gregorian date
now = datetime.now()
current_gregorian_date = convert.Gregorian(now.year, now.month, now.day)

# Convert the current Gregorian date to Hijri
current_hijri_date = current_gregorian_date.to_hijri()

# Get the Hijri month name and day name
hijri_month_name = current_hijri_date.month_name()
hijri_day_of_week = current_hijri_date.weekday()
hijri_day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
hijri_day_name = hijri_day_names[hijri_day_of_week]

# Print the result
print(f'{hijri_day_name}, {current_hijri_date.day} {hijri_month_name} {current_hijri_date.year} AH')
