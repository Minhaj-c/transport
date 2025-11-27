"""
Routes Serializers
Convert Route and Stop models to JSON for API responses
"""

from rest_framework import serializers
from .models import Route, Stop


class StopSerializer(serializers.ModelSerializer):
    """
    Serializer for Stop model
    Converts Stop object to JSON
    """
    class Meta:
        model = Stop
        fields = [
            'id',
            'name',
            'sequence',
            'distance_from_origin',
            'is_limited_stop'
        ]


class RouteSerializer(serializers.ModelSerializer):
    """
    Serializer for Route model
    Includes nested stops information
    """
    stops = StopSerializer(many=True, read_only=True)
    
    class Meta:
        model = Route
        fields = [
            'id',
            'number',
            'name',
            'description',
            'origin',
            'destination',
            'total_distance',
            'duration',
            'stops'
        ]


class RouteListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for route list (without stops)
    Used for dropdown/list views
    """
    class Meta:
        model = Route
        fields = [
            'id',
            'number',
            'name',
            'origin',
            'destination',
            'total_distance'
        ]