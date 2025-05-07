from django.contrib import admin
from .models import Member

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'room_number', 'telephone_number', 'created_at')
    search_fields = ('name', 'email', 'room_number', 'telephone_number')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'email'),
            'description': 'Basic member information'
        }),
        ('Contact Details', {
            'fields': ('room_number', 'telephone_number'),
            'description': 'Member contact information'
        }),
    )
    
    readonly_fields = ('created_at',)
