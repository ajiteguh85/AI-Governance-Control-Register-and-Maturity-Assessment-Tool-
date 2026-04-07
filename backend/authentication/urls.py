from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

app_name = 'authentication'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('me/', views.current_user, name='current-user'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('change-password/', views.change_password, name='change-password'),
    path('users/', views.UserListView.as_view(), name='user-list'),
]
