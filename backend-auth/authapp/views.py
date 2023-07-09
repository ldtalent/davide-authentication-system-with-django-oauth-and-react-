from rest_framework import generics
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Profile
from .serializers import ProfileSerializer, UserSerializer, PasswordUpdateSerializer, ProfileCreateSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response(status=status.HTTP_205_RESET_CONTENT)
            else:
                return Response({"error": "refresh_token not provided."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class HomeView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        content = {'message': 'Welcome to the JWT Authentication page using React Js and Django!'}
        return Response(content)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_serializer = UserSerializer(request.user)
        profile_serializer = ProfileSerializer(request.user.profile)
        data = {
            'user': user_serializer.data,
            'profile': profile_serializer.data
        }
        return Response(data)


class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        try:
            user_data = request.data['user']
            profile_data = request.data['profile']
        except KeyError as e:
            error_message = f"KeyError: {str(e)}"
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        user_serializer = UserSerializer(user, data=user_data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        profile = user.profile
        profile_serializer = ProfileSerializer(profile, data=profile_data, partial=True)
        if profile_serializer.is_valid():
            profile_serializer.save()
        else:
            return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = {
            'user': user_serializer.data,
            'profile': profile_serializer.data
        }
        return Response(data)


class ProfileCreateView(generics.CreateAPIView):
    model = Profile
    queryset = Profile.objects.all()
    serializer_class = ProfileCreateSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.save()  # Manually trigger the save method to generate the thumbnail


class PasswordUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordUpdateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password updated successfully."})
        return Response(serializer.errors, status=400)