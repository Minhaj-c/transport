"""
PreInforms Serializers
"""

from rest_framework import serializers
from .models import PreInform
from routes.models import Stop
from routes.serializers import RouteSerializer, StopSerializer


class PreInformSerializer(serializers.ModelSerializer):
    """
    Serializer for PreInform model
    """
    route_details = RouteSerializer(source='route', read_only=True)
    stop_details = StopSerializer(source='boarding_stop', read_only=True)
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = PreInform
        fields = [
            'id',
            'user',
            'user_name',
            'route',
            'route_details',
            'date_of_travel',
            'desired_time',
            'boarding_stop',
            'stop_details',
            'passenger_count',
            'status',
            'created_at'
        ]
        read_only_fields = ['id', 'user', 'status', 'created_at']
    
    def get_user_name(self, obj):
        """Get user's full name or email"""
        return obj.user.get_full_name()
    
    def validate(self, data):
        """
        Custom validation to ensure boarding stop belongs to route
        """
        route = data.get('route')
        boarding_stop = data.get('boarding_stop')
        
        if boarding_stop and boarding_stop not in route.stops.all():
            raise serializers.ValidationError(
                "The selected boarding stop does not belong to this route."
            )
        
        return data


class PreInformCreateSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for creating pre-informs
    """
    class Meta:
        model = PreInform
        fields = [
            'route',
            'date_of_travel',
            'desired_time',
            'boarding_stop',
            'passenger_count'
        ]