"""
Script to create initial available days for appointments
"""
import os
import django
import datetime

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_records.settings')
django.setup()

from appointments.models import AvailableDay

# Delete any existing records
AvailableDay.objects.all().delete()

# Create AvailableDay records for Monday through Friday (9 AM - 5 PM)
days = [
    (0, 'Monday'),
    (1, 'Tuesday'),
    (2, 'Wednesday'),
    (3, 'Thursday'),
    (4, 'Friday'),
]

for day_number, day_name in days:
    # Create available day
    available_day = AvailableDay.objects.create(
        day_of_week=day_number,
        start_time=datetime.time(9, 0),  # 9:00 AM
        end_time=datetime.time(17, 0),   # 5:00 PM
        slot_duration=30,                # 30-minute slots
        is_active=True
    )
    print(f"Created {day_name} availability: {available_day}")

print("\nAvailable days created successfully!")
print(f"Total available days: {AvailableDay.objects.count()}")
print(f"Total time slots: {sum(len(day.get_time_slots()) for day in AvailableDay.objects.all())}")

