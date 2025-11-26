from django.contrib import admin

# Register your models here.
"""
PreInforms Admin Configuration
"""

from django.contrib import admin
from .models import PreInform


@admin.register(PreInform)
class PreInformAdmin(admin.ModelAdmin):
    """
    Admin configuration for PreInform model
    """
    list_display = (
        'user',
        'route',
        'date_of_travel',
        'desired_time',
        'boarding_stop',
        'passenger_count',
        'status',
        'created_at'
    )
    list_filter = ('status', 'date_of_travel', 'route', 'created_at')
    search_fields = (
        'user__email',
        'route__number',
        'route__name',
        'boarding_stop__name'
    )
    date_hierarchy = 'date_of_travel'
    ordering = ('-created_at',)
    
    # Allow editing status from list view
    list_editable = ('status',)
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Travel Details', {
            'fields': ('route', 'boarding_stop', 'date_of_travel', 'desired_time', 'passenger_count')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        """Optimize queries"""
        return super().get_queryset(request).select_related('user', 'route', 'boarding_stop')