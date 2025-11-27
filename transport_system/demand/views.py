"""
Demand Alerts API Views
"""

from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import render
from django.utils import timezone
from .models import DemandAlert
from .serializers import DemandAlertSerializer, DemandAlertCreateSerializer
from routes.models import Stop


class DemandAlertCreateView(generics.CreateAPIView):
    """
    API endpoint for users to report demand at stops
    
    POST /api/demand-alerts/
    {
        "stop": 5,
        "number_of_people": 25
    }
    """
    queryset = DemandAlert.objects.all()
    serializer_class = DemandAlertCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        """Set the user to currently logged-in user"""
        serializer.save(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Return full details
        output_serializer = DemandAlertSerializer(serializer.instance)
        
        return Response(
            {
                'success': True,
                'message': 'Demand alert submitted successfully',
                'data': output_serializer.data
            },
            status=status.HTTP_201_CREATED
        )


class DemandAlertListView(generics.ListAPIView):
    """
    API endpoint to list demand alerts
    
    GET /api/demand-alerts/
    Optional params:
    - stop_id: Filter by stop
    - route_id: Filter by route
    - status: Filter by status
    - active_only: Show only active alerts (true/false)
    """
    serializer_class = DemandAlertSerializer
    
    def get_queryset(self):
        queryset = DemandAlert.objects.all().select_related(
            'user', 'stop', 'stop__route'
        )
        
        # Apply filters
        stop_id = self.request.query_params.get('stop_id')
        route_id = self.request.query_params.get('route_id')
        status_param = self.request.query_params.get('status')
        active_only = self.request.query_params.get('active_only', 'false').lower() == 'true'
        
        if stop_id:
            queryset = queryset.filter(stop_id=stop_id)
        if route_id:
            queryset = queryset.filter(stop__route_id=route_id)
        if status_param:
            queryset = queryset.filter(status=status_param)
        if active_only:
            # Only show alerts that haven't expired
            queryset = queryset.filter(
                expires_at__gt=timezone.now(),
                status__in=['reported', 'verified', 'dispatched']
            )
        
        return queryset.order_by('-created_at')


@api_view(['GET'])
def active_demand_alerts_view(request):
    """
    Get all currently active demand alerts
    
    GET /api/demand-alerts/active/
    """
    active_alerts = DemandAlert.objects.filter(
        expires_at__gt=timezone.now(),
        status__in=['reported', 'verified', 'dispatched']
    ).select_related('stop', 'stop__route').order_by('-created_at')
    
    serializer = DemandAlertSerializer(active_alerts, many=True)
    
    return Response({
        'total_active_alerts': len(serializer.data),
        'alerts': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resolve_demand_alert_view(request, alert_id):
    """
    Mark a demand alert as resolved (Admin only)
    
    POST /api/demand-alerts/<id>/resolve/
    """
    if request.user.role != 'admin':
        return Response(
            {'error': 'Only admins can resolve alerts'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        alert = DemandAlert.objects.get(id=alert_id)
        alert.mark_resolved()
        
        return Response({
            'success': True,
            'message': 'Alert resolved successfully'
        })
        
    except DemandAlert.DoesNotExist:
        return Response(
            {'error': 'Alert not found'},
            status=status.HTTP_404_NOT_FOUND
        )


def demand_alert_page(request):
    """
    Serve the demand alert form page
    """
    stops = Stop.objects.all().select_related('route').order_by('name')
    context = {'stops': stops}
    return render(request, 'demand_alert.html', context)