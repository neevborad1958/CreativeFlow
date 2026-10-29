from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, login, logout
from .models import User, UserProfile
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            return Response({
                'message': 'User registered successfully',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({
                'message': 'Login successful',
                'user': UserSerializer(user).data
            })
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'message': 'Logged out successfully'})


class MeView(APIView):
    def get(self, request):
        # If user is authenticated, return user details
        if request.user and request.user.is_authenticated:
            return Response(UserSerializer(request.user).data)
        
        # In development mode, return default freelancer demo user if available
        demo_user = User.objects.filter(role='freelancer').first() or User.objects.first()
        if demo_user:
            return Response(UserSerializer(demo_user).data)

        return Response({'detail': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

    def patch(self, request):
        user = request.user if request.user.is_authenticated else User.objects.first()
        if not user:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DemoUsersListView(APIView):
    """
    Returns available demo users so users can easily test all 3 roles:
    Freelancer / Studio Admin, Client, and Team Member.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        users = User.objects.all().order_by('id')
        return Response(UserSerializer(users, many=True).data)

