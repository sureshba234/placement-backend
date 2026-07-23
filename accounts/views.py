from rest_framework import generics, permissions
from .serializers import UserProfileSerializer
from .serializers import ProfileUpdateSerializer


class MeView(generics.RetrieveAPIView):
    """Returns the currently authenticated user's profile, including role."""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UpdateProfileView(generics.UpdateAPIView):
    """Authenticated user updates their own profile fields."""
    serializer_class = ProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['patch']

    def get_object(self):
        return self.request.user