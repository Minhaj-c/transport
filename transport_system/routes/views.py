"""
Routes API Views
"""

from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render
from .models import Route, Stop
from .serializers import RouteSerializer, RouteListSerializer, StopSerializer


@api_view(['GET'])
def api_welcome(request):
    """
    Welcome message for API root
    
    GET /api/
    """
    return Response({
        'message': 'Welcome to Transport Management API',
        'version': '1.0',
        'endpoints': {
            'auth': {
                'signup': '/api/signup/',
                'login': '/api/login/',
                'logout': '/api/logout/',
                'profile': '/api/profile/',
            },
            'routes': {
                'list': '/api/routes/',
                'detail': '/api/routes/<id>/',
                'stops': '/api/routes/<id>/stops/',
            },
            'schedules': {
                'list': '/api/schedules/',
                'driver': '/api/schedules/driver/',
            },
            'preinforms': {
                'create': '/api/preinforms/',
                'list': '/api/preinforms/',
            },
            'demand': {
                'create': '/api/demand-alerts/',
                'list': '/api/demand-alerts/',
            },
        }
    })


class RouteListView(generics.ListAPIView):
    """
    API view to list all bus routes
    
    GET /api/routes/
    """
    queryset = Route.objects.all().prefetch_related('stops')
    serializer_class = RouteSerializer
    
    def get_queryset(self):
        """
        Optionally filter routes by origin or destination
        """
        queryset = super().get_queryset()
        
        origin = self.request.query_params.get('origin')
        destination = self.request.query_params.get('destination')
        
        if origin:
            queryset = queryset.filter(origin__icontains=origin)
        if destination:
            queryset = queryset.filter(destination__icontains=destination)
        
        return queryset


class RouteDetailView(generics.RetrieveAPIView):
    """
    API view to get single route details
    
    GET /api/routes/<id>/
    """
    queryset = Route.objects.all().prefetch_related('stops')
    serializer_class = RouteSerializer


@api_view(['GET'])
def route_stops_view(request, route_id):
    """
    API view to get all stops for a specific route
    
    GET /api/routes/<route_id>/stops/
    """
    try:
        route = Route.objects.get(id=route_id)
        stops = route.stops.all().order_by('sequence')
        serializer = StopSerializer(stops, many=True)
        
        return Response({
            'route': {
                'id': route.id,
                'number': route.number,
                'name': route.name
            },
            'stops': serializer.data
        })
    except Route.DoesNotExist:
        return Response(
            {'error': 'Route not found'},
            status=status.HTTP_404_NOT_FOUND
        )


def homepage(request):
    """
    Serve the main frontend page
    """
    return render(request, 'homepage.html')