"""
Schedules Admin Configuration
"""

from django.contrib import admin
from .models import Bus, Schedule, BusSchedule


@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    """
    Admin configuration for Bus model
    """
    list_display = (
        'number_plate',
        'capacity',
        'mileage',
        'service_type',
        'is_active',
        'is_running',
        'current_route',
        'last_location_update'
    )
    list_filter = ('is_active', 'is_running', 'service_type')
    search_fields = ('number_plate',)
    readonly_fields = ('last_location_update',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('number_plate', 'capacity', 'mileage', 'service_type')
        }),
        ('Status', {
            'fields': ('is_active', 'is_running')
        }),
        ('Current Assignment', {
            'fields': ('current_route', 'current_schedule')
        }),
        ('Location Tracking', {
            'fields': ('current_latitude', 'current_longitude', 'last_location_update'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    """
    Admin configuration for Schedule model
    """
    list_display = (
        'route',
        'bus',
        'driver',
        'date',
        'departure_time',
        'arrival_time',
        'available_seats',
        'total_seats',
        'occupancy_rate'
    )
    list_filter = ('date', 'route', 'bus')
    search_fields = (
        'route__number',
        'route__name',
        'bus__number_plate',
        'driver__email'
    )
    date_hierarchy = 'date'
    ordering = ('-date', 'departure_time')
    
    fieldsets = (
        ('Assignment', {
            'fields': ('route', 'bus', 'driver')
        }),
        ('Timing', {
            'fields': ('date', 'departure_time', 'arrival_time')
        }),
        ('Seat Management', {
            'fields': ('total_seats', 'available_seats')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def occupancy_rate(self, obj):
        """Calculate and display occupancy rate"""
        if obj.total_seats > 0:
            occupied = obj.total_seats - obj.available_seats
            rate = (occupied / obj.total_seats) * 100
            return f"{rate:.1f}%"
        return "0%"
    occupancy_rate.short_description = 'Occupancy'
    
    def get_queryset(self, request):
        """Optimize queries"""
        return super().get_queryset(request).select_related('route', 'bus', 'driver')


@admin.register(BusSchedule)
class BusScheduleAdmin(admin.ModelAdmin):
    """
    Admin configuration for BusSchedule model
    """
    list_display = (
        'bus',
        'route',
        'date',
        'start_time',
        'end_time',
        'duration_hours'
    )
    list_filter = ('date', 'bus', 'route')
    search_fields = ('bus__number_plate', 'route__number')
    date_hierarchy = 'date'
    ordering = ('-date', 'start_time')
    
    fieldsets = (
        ('Assignment', {
            'fields': ('bus', 'route')
        }),
        ('Timing', {
            'fields': ('date', 'start_time', 'end_time')
        }),
    )