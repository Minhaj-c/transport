"""
User Authentication API Views - FIXED FOR MOBILE
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.db import IntegrityError

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])  # Allow anyone to signup
def signup_view(request):
    """
    API endpoint for user registration
    
    POST /api/signup/
    {
        "email": "user@example.com",
        "password": "password123",
        "first_name": "John",
        "last_name": "Doe",
        "role": "passenger"  // or "driver"
    }
    """
    try:
        data = request.data
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        role = data.get('role', 'passenger')
        
        # Validate required fields
        if not email or not password:
            return Response(
                {'error': 'Email and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'User with this email already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create new user
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        
        return Response({
            'success': True,
            'message': 'User created successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role
            }
        }, status=status.HTTP_201_CREATED)
        
    except IntegrityError:
        return Response(
            {'error': 'User with this email already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([AllowAny])  # Allow anyone to login
def login_view(request):
    """
    API endpoint for user login - MOBILE OPTIMIZED
    
    POST /api/login/
    {
        "email": "user@example.com",
        "password": "password123"
    }
    """
    try:
        data = request.data
        email = data.get('email')
        password = data.get('password')
        
        print(f"Login attempt for: {email}")  # Debug log
        
        if not email or not password:
            return Response(
                {'error': 'Email and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Authenticate user
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            # Login the user (creates session)
            login(request, user)
            
            # IMPORTANT: Save session to get session_key
            request.session.save()
            
            print(f"User logged in: {user.email}")  # Debug log
            print(f"Session key: {request.session.session_key}")  # Debug log
            
            # Create response
            response = Response({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role
                }
            }, status=status.HTTP_200_OK)
            
            # CRITICAL: Explicitly set session cookie for mobile apps
            # This ensures Flutter can access the session
            response.set_cookie(
                key='sessionid',
                value=request.session.session_key,
                max_age=86400 * 7,  # 7 days
                httponly=False,      # Allow JavaScript/Flutter to read
                secure=False,        # Set True only with HTTPS
                samesite='Lax',      # Required for mobile apps
                domain=None,         # Use default domain
                path='/'
            )
            
            # Also set CSRF token cookie
            response.set_cookie(
                key='csrftoken',
                value=request.META.get('CSRF_COOKIE', ''),
                max_age=86400 * 7,
                httponly=False,
                secure=False,
                samesite='Lax',
                path='/'
            )
            
            print("Cookies set successfully")  # Debug log
            
            return response
        else:
            print(f"Authentication failed for: {email}")  # Debug log
            return Response(
                {'error': 'Invalid email or password'},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
    except Exception as e:
        print(f"Login error: {str(e)}")  # Debug log
        return Response(
            {'error': f'An error occurred: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
def logout_view(request):
    """
    API endpoint for user logout
    
    POST /api/logout/
    """
    print(f"Logout request from: {request.user.email if request.user.is_authenticated else 'Anonymous'}")
    
    logout(request)
    
    response = Response({
        'success': True,
        'message': 'Logged out successfully'
    }, status=status.HTTP_200_OK)
    
    # Clear cookies
    response.delete_cookie('sessionid')
    response.delete_cookie('csrftoken')
    
    return response


@api_view(['GET'])
def user_profile_view(request):
    """
    API endpoint to get current user profile
    
    GET /api/profile/
    """
    print(f"Profile request - Authenticated: {request.user.is_authenticated}")
    
    if not request.user.is_authenticated:
        return Response(
            {'error': 'Authentication required'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    user = request.user
    return Response({
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': user.role,
        'date_joined': user.date_joined
    }, status=status.HTTP_200_OK)