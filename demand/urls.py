"""
Demand Alerts URL Configuration
"""

from django.urls import path
from . import views

urlpatterns = [
    # Web pages
    path('demand-alert/', views.demand_alert_page, name='demand-alert-page'),
    
    # API endpoints
    path('api/demand-alerts/', views.DemandAlertCreateView.as_view(), name='demand-alert-create'),
    path('api/demand-alerts/list/', views.DemandAlertListView.as_view(), name='demand-alert-list'),
    path('api/demand-alerts/active/', views.active_demand_alerts_view, name='active-demand-alerts'),
    path('api/demand-alerts/<int:alert_id>/resolve/', views.resolve_demand_alert_view, name='resolve-demand-alert'),
]