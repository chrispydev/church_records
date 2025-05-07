from django import forms
from django.utils import timezone
import datetime
from .models import Appointment, AvailableDay, BookingSettings

class AppointmentForm(forms.ModelForm):
    """Form for booking public appointments"""
    
    # Fields with custom widgets
    appointment_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'required': True
        }),
        help_text="Select an available date for your appointment."
    )
    
    appointment_time = forms.TimeField(
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True
        }),
        help_text="Choose an available time slot."
    )
    
    class Meta:
        model = Appointment
        fields = [
            'name', 'email', 'phone', 
            'appointment_date', 'appointment_time', 
            'purpose', 'additional_notes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your full name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your email address',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your phone number',
                'required': True
            }),
            'purpose': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'What would you like to discuss?',
                'required': True
            }),
            'additional_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Any additional information you would like to share',
                'rows': 3
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set the minimum date to today
        today = datetime.date.today()
        self.fields['appointment_date'].widget.attrs['min'] = today.strftime('%Y-%m-%d')
        
        # Make the appointment_time field a select field initially with empty choices
        # The choices will be populated via JavaScript after a date is selected
        self.fields['appointment_time'].widget.choices = [
            ('', 'Select a date first to see available times')
        ]
    
    def clean(self):
        """Validate the appointment details"""
        cleaned_data = super().clean()
        appointment_date = cleaned_data.get('appointment_date')
        appointment_time = cleaned_data.get('appointment_time')
        
        # Check if the system is enabled
        booking_settings = BookingSettings.get_settings()
        if not booking_settings.is_enabled:
            raise forms.ValidationError(
                "The appointment booking system is currently disabled. Please try again later."
            )
        
        # Validation for date
        if appointment_date:
            # Check if date is in the past
            today = datetime.date.today()
            if appointment_date < today:
                self.add_error('appointment_date', "Appointment date cannot be in the past.")
            
            # Check if the day is available
            day_of_week = appointment_date.weekday()
            available_days = AvailableDay.objects.filter(
                day_of_week=day_of_week,
                is_active=True
            )
            
            if not available_days.exists():
                day_name = dict(AvailableDay.DAYS_OF_WEEK)[day_of_week]
                self.add_error('appointment_date', 
                              f"Appointments are not available on {day_name}s. "
                              "Please select another day.")
        
        # Validation for time
        if appointment_date and appointment_time:
            # Check if the selected time is valid for the day
            valid_slot = False
            available_days = AvailableDay.objects.filter(
                day_of_week=appointment_date.weekday(),
                is_active=True
            )
            
            for day in available_days:
                time_slots = day.get_time_slots()
                for slot_time in time_slots:
                    # Compare hours and minutes (ignore seconds)
                    if (slot_time.hour == appointment_time.hour and 
                        slot_time.minute == appointment_time.minute):
                        valid_slot = True
                        break
                
                if valid_slot:
                    break
            
            if not valid_slot:
                self.add_error('appointment_time', 
                              "The selected time slot is not available. "
                              "Please select a different time.")
            
            # Check if the time slot is already booked
            existing_appointments = Appointment.objects.filter(
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                status__in=['pending', 'approved']
            )
            
            if existing_appointments.exists():
                self.add_error('appointment_time', 
                              "This time slot is already booked. "
                              "Please select another time.")
        
        return cleaned_data
    
    def get_available_days(self):
        """Return a list of available days for the next 30 days"""
        available_days = []
        today = datetime.date.today()
        
        # Check the next 30 days
        for i in range(30):
            check_date = today + datetime.timedelta(days=i)
            day_of_week = check_date.weekday()
            
            # Check if this day of week is available
            if AvailableDay.objects.filter(day_of_week=day_of_week, is_active=True).exists():
                available_days.append({
                    'date': check_date,
                    'day_name': check_date.strftime('%A'),
                    'formatted': check_date.strftime('%Y-%m-%d')
                })
        
        return available_days
    
    def get_time_slots_for_day(self, date):
        """Return available time slots for a specific date"""
        if not date:
            return []
        
        # Convert string to date if needed
        if isinstance(date, str):
            try:
                date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
            except ValueError:
                return []
        
        day_of_week = date.weekday()
        available_slots = []
        
        # Get all available day configurations for this day of week
        available_days = AvailableDay.objects.filter(
            day_of_week=day_of_week,
            is_active=True
        )
        
        # Get all booked slots for this date to exclude them
        booked_times = Appointment.objects.filter(
            appointment_date=date,
            status__in=['pending', 'approved']
        ).values_list('appointment_time', flat=True)
        
        # Generate all possible time slots
        for day in available_days:
            time_slots = day.get_time_slots()
            
            for slot_time in time_slots:
                # Check if this slot is already booked
                is_booked = False
                for booked_time in booked_times:
                    if (slot_time.hour == booked_time.hour and 
                        slot_time.minute == booked_time.minute):
                        is_booked = True
                        break
                
                if not is_booked:
                    formatted_time = slot_time.strftime('%I:%M %p')
                    value = slot_time.strftime('%H:%M')
                    available_slots.append({
                        'time': slot_time,
                        'formatted': formatted_time,
                        'value': value
                    })
        
        return available_slots

