from django.urls import path
from .views import AuthorizationAPIView, RegistrationAPIView, ConfirmUserAPIView, CustomTokenObtainPairView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView
)

urlpatterns = [
    path('auth/', AuthorizationAPIView.as_view(), name='auth'),
    path('register/', RegistrationAPIView.as_view(), name='register'),
    path('confirm/', ConfirmUserAPIView.as_view(), name='confirm'),


    path('jwt/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('jwt/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('jwt/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]