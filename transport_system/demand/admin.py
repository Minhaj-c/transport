"""
Demand Alerts Admin Configuration
"""

from django.contrib import admin
from django.utils import timezone
from .models import DemandAlert


@admin.register(DemandAlert)
class DemandAlertAdmin(admin.ModelAdmin):
    """
    Admin configuration for DemandAlert model
    """
    list_display = (
        'user',
        'stop',
        'number_of_people',
        'status',
        'created_at',
        'expires_at',
        'is_active_status',
        'time_remaining'
    )
    list_filter = ('status', 'stop__route', 'created_at')
    search_fields = (
        'user__email',
        'stop__name',
        'stop__route__number'
    )
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    # Allow editing status from list view
    list_editable = ('status',)
    
    fieldsets = (
        ('Alert Information', {
            'fields': ('user', 'stop', 'number_of_people')
        }),
        ('Status', {
            'fields': ('status', 'admin_notes')
        }),
        ('Timing', {
            'fields': ('created_at', 'expires_at', 'resolved_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'expires_at', 'resolved_at')
    
    def is_active_status(self, obj):
        """Display if alert is still active"""
        return obj.is_active()
    is_active_status.short_description = 'Active'
    is_active_status.boolean = True
    
    def time_remaining(self, obj):
        """Display time remaining before expiry"""
        if obj.is_active():
            remaining = obj.expires_at - timezone.now()
            minutes = int(remaining.total_seconds() / 60)
            if minutes > 0:
                return f"{minutes} min"
            return "Expiring soon"
        return "Expired"
    time_remaining.short_description = 'Time Left'
    
    def get_queryset(self, request):
        """Optimize queries"""
        return super().get_queryset(request).select_related('user', 'stop', 'stop__route')
    
    actions = ['mark_as_dispatched', 'mark_as_resolved']
    
    def mark_as_dispatched(self, request, queryset):
        """Bulk action to mark alerts as dispatched"""
        updated = queryset.update(status='dispatched')
        self.message_user(request, f"{updated} alert(s) marked as dispatched.")
    mark_as_dispatched.short_description = "Mark selected as Dispatched"
    
    def mark_as_resolved(self, request, queryset):
        """Bulk action to mark alerts as resolved"""
        count = 0
        for alert in queryset:
            alert.mark_resolved()
            count += 1
        self.message_user(request, f"{count} alert(s) marked as resolved.")
    mark_as_resolved.short_description = "Mark selected as Resolved"