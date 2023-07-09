
from django.urls import path
from .views import ProfileCreateView, ProfileView, ProfileUpdateView, PasswordUpdateView, LogoutView, HomeView

urlpatterns = [
path('register/', ProfileCreateView.as_view(), name='register'),
path('profile/', ProfileView.as_view(), name='profile'),
path('profile/update/', ProfileUpdateView.as_view(), name='profile-update'),
path('profile/password/update/', PasswordUpdateView.as_view(), name='password-update'),
    path('', HomeView.as_view(), name='home'),
    path('logout/', LogoutView.as_view(), name='logout')
]
