"""
Demand Alerts Serializers
"""

from rest_framework import serializers
from .models import DemandAlert
from routes.serializers import StopSerializer


class DemandAlertSerializer(serializers.ModelSerializer):
    """
    Serializer for DemandAlert model
    """
    stop_details = StopSerializer(source='stop', read_only=True)
    user_name = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    time_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = DemandAlert
        fields = [
            'id',
            'user',
            'user_name',
            'stop',
            'stop_details',
            'number_of_people',
            'status',
            'created_at',
            'expires_at',
            'is_active',
            'time_remaining'
        ]
        read_only_fields = ['id', 'user', 'status', 'created_at', 'expires_at']
    
    def get_user_name(self, obj):
        """Get user's full name or email"""
        return obj.user.get_full_name()
    
    def get_is_active(self, obj):
        """Check if alert is still active"""
        return obj.is_active()
    
    def get_time_remaining(self, obj):
        """Calculate time remaining in minutes"""
        if obj.is_active():
            from django.utils import timezone
            remaining = obj.expires_at - timezone.now()
            return int(remaining.total_seconds() / 60)
        return 0


class DemandAlertCreateSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for creating demand alerts
    """
    class Meta:
        model = DemandAlert
        fields = [
            'stop',
            'number_of_people'
        ]