from django.db import models
from django.core.exceptions import ValidationError
import datetime

class BookingSettings(models.Model):
    """Global settings for the appointment booking system"""
    is_enabled = models.BooleanField(default=True, verbose_name="Enable Booking System")
    booking_instructions = models.TextField(blank=True, help_text="Instructions shown to users on the booking page")
    
    class Meta:
        verbose_name = 'Booking Settings'
        verbose_name_plural = 'Booking Settings'
    
    def save(self, *args, **kwargs):
        """Ensure only one instance of BookingSettings exists"""
        if not self.pk and BookingSettings.objects.exists():
            raise ValidationError('There can only be one booking settings instance')
        return super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get or create booking settings"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
    
    def __str__(self):
        status = "Enabled" if self.is_enabled else "Disabled"
        return f"Booking System: {status}"


class AvailableDay(models.Model):
    """Days and time slots available for booking"""
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK, verbose_name="Day")
    start_time = models.TimeField(verbose_name="Start Time")
    end_time = models.TimeField(verbose_name="End Time")
    slot_duration = models.IntegerField(
        default=30, 
        verbose_name="Slot Duration (minutes)",
        help_text="Duration of each appointment slot in minutes"
    )
    is_active = models.BooleanField(default=True, verbose_name="Active")
    
    class Meta:
        ordering = ['day_of_week', 'start_time']
        verbose_name = 'Available Day'
        verbose_name_plural = 'Available Days'
        unique_together = ['day_of_week', 'start_time', 'end_time']
    
    def clean(self):
        """Validate time slots"""
        if self.start_time >= self.end_time:
            raise ValidationError('End time must be after start time')
        
        # Calculate total minutes
        start_minutes = self.start_time.hour * 60 + self.start_time.minute
        end_minutes = self.end_time.hour * 60 + self.end_time.minute
        total_minutes = end_minutes - start_minutes
        
        if total_minutes < self.slot_duration:
            raise ValidationError('Time range is too short for the specified slot duration')
    
    def get_time_slots(self):
        """Generate all time slots for this day based on duration"""
        slots = []
        
        # Calculate minutes
        start_minutes = self.start_time.hour * 60 + self.start_time.minute
        end_minutes = self.end_time.hour * 60 + self.end_time.minute
        current_minutes = start_minutes
        
        while current_minutes + self.slot_duration <= end_minutes:
            # Convert minutes to time
            hours = current_minutes // 60
            minutes = current_minutes % 60
            slot_time = datetime.time(hours, minutes)
            
            slots.append(slot_time)
            current_minutes += self.slot_duration
        
        return slots
    
    def __str__(self):
        return f"{self.get_day_of_week_display()}: {self.start_time.strftime('%I:%M %p')} - {self.end_time.strftime('%I:%M %p')}"


class Appointment(models.Model):
    """Public appointment bookings"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Full Name")
    email = models.EmailField(verbose_name="Email Address")
    phone = models.CharField(max_length=20, verbose_name="Phone Number")
    appointment_date = models.DateField(verbose_name="Date")
    appointment_time = models.TimeField(verbose_name="Time")
    purpose = models.CharField(
        max_length=100, 
        verbose_name="Purpose of Meeting",
        help_text="Brief description of what you would like to discuss"
    )
    additional_notes = models.TextField(
        blank=True, 
        verbose_name="Additional Notes",
        help_text="Any additional information you would like to provide"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Status"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['appointment_date', 'appointment_time']
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'
    
    def clean(self):
        """Validate appointment date and time"""
        # Check if booking system is enabled
        booking_settings = BookingSettings.get_settings()
        if not booking_settings.is_enabled:
            raise ValidationError("The booking system is currently disabled.")
        
        # Check if date is in the past
        if self.appointment_date < datetime.date.today():
            raise ValidationError("Appointment date cannot be in the past.")
        
        # Check if day is available
        day_of_week = self.appointment_date.weekday()
        available_days = AvailableDay.objects.filter(
            day_of_week=day_of_week,
            is_active=True
        )
        
        if not available_days.exists():
            day_name = dict(AvailableDay.DAYS_OF_WEEK)[day_of_week]
            raise ValidationError(f"Appointments are not available on {day_name}s.")
        
        # Check if time slot is valid
        valid_slot = False
        for day in available_days:
            time_slots = day.get_time_slots()
            for slot_time in time_slots:
                if slot_time == self.appointment_time:
                    valid_slot = True
                    break
            
            if valid_slot:
                break
        
        if not valid_slot:
            raise ValidationError("The selected time slot is not available.")
        
        # Check if slot is already booked
        existing_appointments = Appointment.objects.filter(
            appointment_date=self.appointment_date,
            appointment_time=self.appointment_time,
            status__in=['pending', 'approved']
        ).exclude(pk=self.pk)
        
        if existing_appointments.exists():
            raise ValidationError("This time slot is already booked. Please select another time.")
    
    def is_active(self):
        """Check if appointment is active (not cancelled and in the future)"""
        return (
            self.status != 'cancelled' and 
            (self.appointment_date > datetime.date.today() or 
             (self.appointment_date == datetime.date.today() and 
              self.appointment_time > datetime.datetime.now().time()))
        )
    
    def can_cancel(self):
        """Check if appointment can be cancelled"""
        return self.status != 'cancelled' and self.is_active()
    
    def cancel(self):
        """Cancel the appointment"""
        self.status = 'cancelled'
        self.save()
    
    def __str__(self):
        return f"{self.name} - {self.appointment_date.strftime('%Y-%m-%d')} at {self.appointment_time.strftime('%I:%M %p')}"
