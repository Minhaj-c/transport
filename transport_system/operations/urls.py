"""
Operations URL Configuration
"""

from django.urls import path
from . import views

urlpatterns = [
    # Web pages
    path('admin-dashboard/', views.admin_dashboard, name='admin-dashboard'),
    path('generate-report/', views.generate_weekly_report_view, name='generate-report'),
    path('analytics/', views.analytics_dashboard, name='analytics-dashboard'),
]