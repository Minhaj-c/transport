"""
PreInforms URL Configuration
"""

from django.urls import path
from . import views

urlpatterns = [
    # Web pages
    path('preinform-form/', views.preinform_form_page, name='preinform-form-page'),
    
    # API endpoints
    path('api/preinforms/', views.PreInformCreateView.as_view(), name='preinform-create'),
    path('api/preinforms/list/', views.PreInformListView.as_view(), name='preinform-list'),
    path('api/preinforms/my/', views.my_preinforms_view, name='my-preinforms'),
    path('api/preinforms/<int:preinform_id>/cancel/', views.cancel_preinform_view, name='cancel-preinform'),
]