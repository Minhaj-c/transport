"""
Operations Admin Configuration
"""

from django.contrib import admin
from django.db.models import Sum, Avg
from .models import WeeklyPerformance


@admin.register(WeeklyPerformance)
class WeeklyPerformanceAdmin(admin.ModelAdmin):
    """
    Admin configuration for WeeklyPerformance model
    """
    list_display = (
        'bus',
        'route',
        'week_start_date',
        'total_passengers',
        'total_kms',
        'total_revenue',
        'total_cost',
        'total_profit',
        'profit_status'
    )
    list_filter = ('week_start_date', 'route', 'bus')
    search_fields = ('bus__number_plate', 'route__number')
    date_hierarchy = 'week_start_date'
    ordering = ('-week_start_date',)
    
    fieldsets = (
        ('Assignment', {
            'fields': ('bus', 'route', 'week_start_date')
        }),
        ('Passenger Data', {
            'fields': ('estimated_passengers', 'actual_passengers', 'total_passengers')
        }),
        ('Operations', {
            'fields': ('total_kms',)
        }),
        ('Financial Metrics (Auto-calculated)', {
            'fields': ('total_revenue', 'total_cost', 'total_profit'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = (
        'total_passengers',
        'total_revenue',
        'total_cost',
        'total_profit',
        'created_at',
        'updated_at'
    )
    
    def profit_status(self, obj):
        """Display profit status with color"""
        if obj.total_profit > 0:
            return "✓ Profitable"
        elif obj.total_profit < 0:
            return "✗ Loss"
        return "⚬ Break-even"
    profit_status.short_description = 'Status'
    
    def get_queryset(self, request):
        """Optimize queries"""
        return super().get_queryset(request).select_related('bus', 'route')
    
    # Add summary statistics at the bottom
    def changelist_view(self, request, extra_context=None):
        """Add summary statistics to change list"""
        response = super().changelist_view(request, extra_context)
        
        try:
            qs = response.context_data['cl'].queryset
            stats = qs.aggregate(
                total_revenue=Sum('total_revenue'),
                total_cost=Sum('total_cost'),
                total_profit=Sum('total_profit'),
                avg_passengers=Avg('total_passengers'),
            )
            
            response.context_data['summary'] = {
                'total_revenue': stats['total_revenue'] or 0,
                'total_cost': stats['total_cost'] or 0,
                'total_profit': stats['total_profit'] or 0,
                'avg_passengers': round(stats['avg_passengers'] or 0, 1),
            }
        except (AttributeError, KeyError):
            pass
        
        return response