from django.shortcuts import render

# Create your views here.
"""
Schedules API Views
"""

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import render
from datetime import timedelta
import math

from .models import Schedule, Bus
from .serializers import ScheduleSerializer, LiveBusSerializer, BusLocationSerializer


class ScheduleListView(generics.ListAPIView):
    """
    API view to list schedules
    
    GET /api/schedules/
    Optional params:
    - route_id: Filter by route
    - date: Filter by date (YYYY-MM-DD)
    - driver_id: Filter by driver
    """
    serializer_class = ScheduleSerializer
    
    def get_queryset(self):
        queryset = Schedule.objects.all().select_related('route', 'bus', 'driver')
        
        # Get filter parameters
        route_id = self.request.query_params.get('route_id')
        date = self.request.query_params.get('date')
        driver_id = self.request.query_params.get('driver_id')
        
        # Apply filters
        if route_id:
            queryset = queryset.filter(route_id=route_id)
        if date:
            queryset = queryset.filter(date=date)
        else:
            # Default to today and future schedules
            today = timezone.now().date()
            queryset = queryset.filter(date__gte=today)
        if driver_id:
            queryset = queryset.filter(driver_id=driver_id)
        
        return queryset.order_by('date', 'departure_time')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def driver_schedules_view(request):
    """
    API view to get schedules for logged-in driver
    
    GET /api/schedules/driver/
    """
    if request.user.role != 'driver':
        return Response(
            {'error': 'Only drivers can access this endpoint'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get driver's schedules for today and future
    today = timezone.now().date()
    schedules = Schedule.objects.filter(
        driver=request.user,
        date__gte=today
    ).select_related('route', 'bus').order_by('date', 'departure_time')
    
    serializer = ScheduleSerializer(schedules, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def nearby_buses(request):
    """
    Get buses near user location
    
    GET /api/buses/nearby/?latitude=11.2588&longitude=75.7804&radius=5
    """
    try:
        user_lat = float(request.GET.get('latitude'))
        user_lng = float(request.GET.get('longitude'))
        radius_km = float(request.GET.get('radius', 5))
    except (TypeError, ValueError):
        return Response({
            'error': 'Invalid coordinates. Provide latitude, longitude, and optional radius.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get buses that are currently running (updated in last 5 minutes)
    five_minutes_ago = timezone.now() - timedelta(minutes=5)
    
    running_buses = Bus.objects.filter(
        is_running=True,
        current_latitude__isnull=False,
        current_longitude__isnull=False,
        last_location_update__gte=five_minutes_ago
    ).select_related('current_route', 'current_schedule')
    
    nearby_buses_list = []
    
    for bus in running_buses:
        distance = calculate_distance(
            user_lat, user_lng,
            float(bus.current_latitude), float(bus.current_longitude)
        )
        
        if distance <= radius_km:
            bus_data = LiveBusSerializer(bus).data
            bus_data['distance_km'] = round(distance, 2)
            nearby_buses_list.append(bus_data)
    
    # Sort by distance
    nearby_buses_list.sort(key=lambda x: x['distance_km'])
    
    return Response({
        'buses': nearby_buses_list,
        'user_location': {'latitude': user_lat, 'longitude': user_lng},
        'search_radius_km': radius_km,
        'total_found': len(nearby_buses_list)
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_bus_location(request):
    """
    Driver endpoint to update bus location
    
    POST /api/buses/update-location/
    {
        "bus_id": 1,
        "latitude": 11.2588,
        "longitude": 75.7804,
        "schedule_id": 5
    }
    """
    # Only drivers can update location
    if request.user.role != 'driver':
        return Response(
            {'error': 'Only drivers can update bus locations'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        latitude = float(request.data.get('latitude'))
        longitude = float(request.data.get('longitude'))
        bus_id = request.data.get('bus_id')
        schedule_id = request.data.get('schedule_id')
    except (TypeError, ValueError):
        return Response(
            {'error': 'Invalid data provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        bus = Bus.objects.get(id=bus_id)
        
        # Update location
        bus.update_location(latitude, longitude)
        bus.is_running = True
        
        # If schedule provided, link it
        if schedule_id:
            try:
                schedule = Schedule.objects.get(id=schedule_id, driver=request.user)
                bus.current_schedule = schedule
                bus.current_route = schedule.route
            except Schedule.DoesNotExist:
                pass
        
        bus.save()
        
        return Response({
            'success': True,
            'message': 'Location updated successfully',
            'bus': BusLocationSerializer(bus).data
        })
        
    except Bus.DoesNotExist:
        return Response(
            {'error': 'Bus not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def bus_details(request, bus_id):
    """
    Get detailed information about a specific bus
    
    GET /api/buses/<bus_id>/
    """
    try:
        bus = Bus.objects.select_related('current_route', 'current_schedule').get(
            id=bus_id,
            is_running=True
        )
        return Response(LiveBusSerializer(bus).data)
    except Bus.DoesNotExist:
        return Response(
            {'error': 'Bus not found or not running'},
            status=status.HTTP_404_NOT_FOUND
        )


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two coordinates using Haversine formula
    Returns distance in kilometers
    """
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    return distance


def schedules_page(request):
    """
    Serve the schedules frontend page
    """
    route_id = request.GET.get('route_id')
    context = {'route_id': route_id}
    return render(request, 'schedules.html', context)