from django.contrib import admin
from django.utils.html import format_html
from .models import BookingSettings, AvailableDay, Appointment

@admin.register(BookingSettings)
class BookingSettingsAdmin(admin.ModelAdmin):
    list_display = ('system_status', 'is_enabled')
    fieldsets = (
        ('System Status', {
            'fields': ('is_enabled',),
            'description': 'Enable or disable the appointment booking system'
        }),
        ('Instructions', {
            'fields': ('booking_instructions',),
            'description': 'Instructions displayed to users on the booking page'
        }),
    )
    actions = None  # Disable actions dropdown
    
    def system_status(self, obj):
        if obj.is_enabled:
            return format_html('<span style="color: green; font-weight: bold;">ENABLED</span>')
        return format_html('<span style="color: red; font-weight: bold;">DISABLED</span>')
    system_status.short_description = 'Booking System Status'
    
    def has_add_permission(self, request):
        # Only allow adding if no settings object exists
        return not BookingSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the settings object
        return False

@admin.register(AvailableDay)
class AvailableDayAdmin(admin.ModelAdmin):
    list_display = ('day_display', 'time_range', 'slot_duration_display', 'slot_count', 'is_active', 'status_display')
    list_filter = ('day_of_week', 'is_active')
    list_editable = ('is_active',)
    actions = ['activate_days', 'deactivate_days']
    
    def day_display(self, obj):
        return obj.get_day_of_week_display()
    day_display.short_description = 'Day'
    day_display.admin_order_field = 'day_of_week'
    
    def time_range(self, obj):
        return f"{obj.start_time.strftime('%I:%M %p')} - {obj.end_time.strftime('%I:%M %p')}"
    time_range.short_description = 'Hours'
    
    def slot_duration_display(self, obj):
        return f"{obj.slot_duration} minutes"
    slot_duration_display.short_description = 'Duration'
    
    def slot_count(self, obj):
        return len(obj.get_time_slots())
    slot_count.short_description = 'Available Slots'
    
    def status_display(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">Active</span>')
        return format_html('<span style="color: red;">Inactive</span>')
    status_display.short_description = 'Status'
    
    def activate_days(self, request, queryset):
        queryset.update(is_active=True)
    activate_days.short_description = "Activate selected days"
    
    def deactivate_days(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_days.short_description = "Deactivate selected days"
    
    fieldsets = (
        ('Day', {
            'fields': ('day_of_week', 'is_active'),
        }),
        ('Time Slots', {
            'fields': ('start_time', 'end_time', 'slot_duration'),
            'description': 'Define the time range and appointment slot duration'
        }),
    )

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'appointment_date', 'appointment_time', 'purpose', 'status_display', 'created_at')
    list_filter = ('status', 'appointment_date')
    search_fields = ('name', 'email', 'phone', 'purpose')
    readonly_fields = ('created_at',)
    actions = ['approve_appointments', 'cancel_appointments']
    date_hierarchy = 'appointment_date'
    
    def status_display(self, obj):
        status_colors = {
            'pending': 'orange',
            'approved': 'green',
            'cancelled': 'red',
        }
        color = status_colors.get(obj.status, 'black')
        return format_html('<span style="color: {};">{}</span>', 
                         color, obj.get_status_display())
    status_display.short_description = 'Status'
    status_display.admin_order_field = 'status'
    
    def approve_appointments(self, request, queryset):
        queryset.update(status='approved')
    approve_appointments.short_description = "Approve selected appointments"
    
    def cancel_appointments(self, request, queryset):
        queryset.update(status='cancelled')
    cancel_appointments.short_description = "Cancel selected appointments"
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Appointment Details', {
            'fields': ('appointment_date', 'appointment_time', 'purpose', 'status')
        }),
        ('Additional Information', {
            'fields': ('additional_notes', 'created_at'),
            'classes': ('collapse',)
        }),
    )
