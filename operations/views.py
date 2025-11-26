"""
Operations and Analytics Views
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from django.db.models import Sum, Count, Avg, Q
from django.contrib import messages
from datetime import timedelta
from .models import WeeklyPerformance
from schedules.models import BusSchedule, Bus
from preinforms.models import PreInform
from routes.models import Route


def admin_check(user):
    """Check if user is authenticated and is admin"""
    return user.is_authenticated and user.role == 'admin'


@user_passes_test(admin_check)
def admin_dashboard(request):
    """
    Main admin dashboard showing weekly performance summary
    
    URL: /admin-dashboard/
    """
    # Calculate the start of last week (Monday)
    today = timezone.now().date()
    start_of_last_week = today - timedelta(days=today.weekday() + 7)
    
    # Get all performance records from last week
    last_week_performances = WeeklyPerformance.objects.filter(
        week_start_date=start_of_last_week
    ).select_related('bus', 'route')
    
    # Calculate totals
    total_profit = sum(p.total_profit for p in last_week_performances)
    total_revenue = sum(p.total_revenue for p in last_week_performances)
    total_cost = sum(p.total_cost for p in last_week_performances)
    total_passengers = sum(p.total_passengers for p in last_week_performances)
    
    # Top performing routes (by profit)
    route_performance = last_week_performances.values(
        'route__number', 'route__name'
    ).annotate(
        total_profit=Sum('total_profit'),
        total_passengers=Sum('total_passengers')
    ).order_by('-total_profit')
    
    # Top performing buses (by profit)
    bus_performance = last_week_performances.values(
        'bus__number_plate'
    ).annotate(
        total_profit=Sum('total_profit'),
        total_routes=Count('id')
    ).order_by('-total_profit')
    
    context = {
        'week_start': start_of_last_week,
        'total_profit': total_profit,
        'total_revenue': total_revenue,
        'total_cost': total_cost,
        'total_passengers': total_passengers,
        'route_performance': route_performance,
        'bus_performance': bus_performance,
        'performances': last_week_performances,
    }
    
    return render(request, 'admin_dashboard.html', context)


@user_passes_test(admin_check)
def generate_weekly_report_view(request):
    """
    Generate weekly performance reports from BusSchedule and PreInform data
    
    URL: /generate-report/
    """
    # Calculate last week's dates
    today = timezone.now().date()
    start_of_last_week = today - timedelta(days=today.weekday() + 7)
    end_of_last_week = start_of_last_week + timedelta(days=6)
    
    report_data = []
    
    # Get all bus assignments from last week
    weekly_assignments = BusSchedule.objects.filter(
        date__gte=start_of_last_week,
        date__lte=end_of_last_week
    ).select_related('bus', 'route')
    
    if not weekly_assignments.exists():
        messages.warning(
            request,
            "No bus assignments found for last week. Create BusSchedule records first."
        )
        return redirect('admin-dashboard')
    
    # Group by bus and route
    from itertools import groupby
    from operator import attrgetter
    
    assignments_sorted = sorted(
        weekly_assignments,
        key=lambda x: (x.bus_id, x.route_id)
    )
    
    for (bus, route), bus_assignments in groupby(
        assignments_sorted,
        key=lambda x: (x.bus, x.route)
    ):
        bus_assignments = list(bus_assignments)
        
        # Calculate total kilometers
        total_kms = sum(
            assignment.route.total_distance
            for assignment in bus_assignments
        )
        
        # Calculate estimated passengers from PreInform
        estimated_passengers = PreInform.objects.filter(
            route=route,
            date_of_travel__gte=start_of_last_week,
            date_of_travel__lte=end_of_last_week
        ).aggregate(total=Sum('passenger_count'))['total'] or 0
        
        # Create or update weekly performance record
        weekly_perf, created = WeeklyPerformance.objects.get_or_create(
            bus=bus,
            route=route,
            week_start_date=start_of_last_week,
            defaults={
                'estimated_passengers': estimated_passengers,
                'total_kms': total_kms,
                'actual_passengers': 0
            }
        )
        
        # If record already exists, update it
        if not created:
            weekly_perf.estimated_passengers = estimated_passengers
            weekly_perf.total_kms = total_kms
            weekly_perf.save()
        
        report_data.append({
            'bus': bus,
            'route': route,
            'estimated_passengers': estimated_passengers,
            'total_kms': total_kms,
            'created': created
        })
    
    messages.success(
        request,
        f"Generated weekly report for {start_of_last_week} to {end_of_last_week}"
    )
    
    return render(request, 'report_generated.html', {
        'report_data': report_data,
        'week_start': start_of_last_week,
        'week_end': end_of_last_week
    })


@user_passes_test(admin_check)
def analytics_dashboard(request):
    """
    Advanced analytics dashboard with trends and patterns
    
    URL: /analytics/
    """
    today = timezone.now().date()
    start_date = today - timedelta(weeks=8)
    
    # 1. Weekly Trends
    weekly_data = WeeklyPerformance.objects.filter(
        week_start_date__gte=start_date
    ).values('week_start_date').distinct()
    
    weekly_trends = []
    for week in weekly_data:
        week_start = week['week_start_date']
        week_data = WeeklyPerformance.objects.filter(week_start_date=week_start)
        
        weekly_trends.append({
            'week_start_date': week_start,
            'total_profit': sum(p.total_profit for p in week_data),
            'total_revenue': sum(p.total_revenue for p in week_data),
            'total_passengers': sum(p.total_passengers for p in week_data),
        })
    
    # Sort by date
    weekly_trends.sort(key=lambda x: x['week_start_date'])
    
    # 2. Route Performance
    route_data = {}
    for performance in WeeklyPerformance.objects.filter(week_start_date__gte=start_date):
        route_key = performance.route.number
        if route_key not in route_data:
            route_data[route_key] = {
                'route__number': performance.route.number,
                'route__name': performance.route.name,
                'total_profit': 0,
                'total_kms': 0,
                'total_passengers': 0,
            }
        
        route_data[route_key]['total_profit'] += float(performance.total_profit)
        route_data[route_key]['total_kms'] += float(performance.total_kms)
        route_data[route_key]['total_passengers'] += performance.total_passengers
    
    # Calculate profit per km
    for route in route_data.values():
        if route['total_kms'] > 0:
            route['profit_per_km'] = route['total_profit'] / route['total_kms']
        else:
            route['profit_per_km'] = 0
    
    route_performance = sorted(
        route_data.values(),
        key=lambda x: x['total_profit'],
        reverse=True
    )[:10]
    
    # 3. Bus Efficiency
    bus_data = {}
    for performance in WeeklyPerformance.objects.filter(week_start_date__gte=start_date):
        bus_key = performance.bus.number_plate
        if bus_key not in bus_data:
            bus_data[bus_key] = {
                'bus__number_plate': performance.bus.number_plate,
                'total_profit': 0,
                'total_revenue': 0,
                'total_kms': 0,
                'total_passengers': 0,
            }
        
        bus_data[bus_key]['total_profit'] += float(performance.total_profit)
        bus_data[bus_key]['total_revenue'] += float(performance.total_revenue)
        bus_data[bus_key]['total_kms'] += float(performance.total_kms)
        bus_data[bus_key]['total_passengers'] += performance.total_passengers
    
    # Calculate revenue per km
    for bus in bus_data.values():
        if bus['total_kms'] > 0:
            bus['revenue_per_km'] = bus['total_revenue'] / bus['total_kms']
        else:
            bus['revenue_per_km'] = 0
    
    bus_efficiency = sorted(
        bus_data.values(),
        key=lambda x: x['revenue_per_km'],
        reverse=True
    )[:10]
    
    # 4. Demand Patterns
    from django.db.models.functions import ExtractHour, ExtractWeekDay
    
    demand_patterns = PreInform.objects.filter(
        created_at__gte=start_date
    ).annotate(
        hour=ExtractHour('desired_time'),
        day_of_week=ExtractWeekDay('date_of_travel')
    ).values('hour', 'day_of_week').annotate(
        demand_count=Count('id')
    ).order_by('day_of_week', 'hour')
    
    context = {
        'weekly_trends': weekly_trends,
        'route_performance': route_performance,
        'bus_efficiency': bus_efficiency,
        'demand_patterns': list(demand_patterns),
    }
    
    return render(request, 'analytics_dashboard.html', context)