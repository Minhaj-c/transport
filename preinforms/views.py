"""
PreInforms API Views
"""

from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import render
from .models import PreInform
from .serializers import PreInformSerializer, PreInformCreateSerializer
from schedules.models import Schedule


class PreInformCreateView(generics.CreateAPIView):
    """
    API endpoint for users to submit pre-informs
    
    POST /api/preinforms/
    {
        "route": 1,
        "date_of_travel": "2024-12-25",
        "desired_time": "09:00",
        "boarding_stop": 5,
        "passenger_count": 2
    }
    """
    queryset = PreInform.objects.all()
    serializer_class = PreInformCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        """Set the user to currently logged-in user"""
        serializer.save(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Return full details with nested objects
        output_serializer = PreInformSerializer(serializer.instance)
        
        return Response(
            {
                'success': True,
                'message': 'Pre-inform submitted successfully',
                'data': output_serializer.data
            },
            status=status.HTTP_201_CREATED
        )


class PreInformListView(generics.ListAPIView):
    """
    API endpoint to list pre-informs
    
    GET /api/preinforms/
    Optional params:
    - user_id: Filter by user
    - route_id: Filter by route
    - date: Filter by travel date
    - status: Filter by status
    """
    serializer_class = PreInformSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = PreInform.objects.all().select_related(
            'user', 'route', 'boarding_stop'
        )
        
        # Admin can see all, users see only their own
        if self.request.user.role != 'admin':
            queryset = queryset.filter(user=self.request.user)
        
        # Apply filters
        user_id = self.request.query_params.get('user_id')
        route_id = self.request.query_params.get('route_id')
        date = self.request.query_params.get('date')
        status_param = self.request.query_params.get('status')
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if route_id:
            queryset = queryset.filter(route_id=route_id)
        if date:
            queryset = queryset.filter(date_of_travel=date)
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        return queryset.order_by('-created_at')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_preinforms_view(request):
    """
    Get pre-informs for currently logged-in user
    
    GET /api/preinforms/my/
    """
    preinforms = PreInform.objects.filter(
        user=request.user
    ).select_related('route', 'boarding_stop').order_by('-created_at')
    
    serializer = PreInformSerializer(preinforms, many=True)
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cancel_preinform_view(request, preinform_id):
    """
    Cancel a pre-inform
    
    DELETE /api/preinforms/<id>/cancel/
    """
    try:
        preinform = PreInform.objects.get(id=preinform_id, user=request.user)
        
        # Only allow cancellation if status is pending
        if preinform.status != 'pending':
            return Response(
                {'error': 'Can only cancel pending pre-informs'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        preinform.status = 'cancelled'
        preinform.save()
        
        return Response({
            'success': True,
            'message': 'Pre-inform cancelled successfully'
        })
        
    except PreInform.DoesNotExist:
        return Response(
            {'error': 'Pre-inform not found'},
            status=status.HTTP_404_NOT_FOUND
        )


def preinform_form_page(request):
    """
    Serve the pre-inform form page
    """
    schedule_id = request.GET.get('schedule_id')
    try:
        schedule = Schedule.objects.get(id=schedule_id)
        context = {'schedule': schedule}
        return render(request, 'preinform_form.html', context)
    except Schedule.DoesNotExist:
        return render(request, 'error.html', {'message': 'Schedule not found'})