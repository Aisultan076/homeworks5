from rest_framework_simplejwt.tokens import RefreshToken
import requests
from django.conf import settings
from rest_framework.views import APIView
from .models import CustomUser
from rest_framework.response import Response

class GoogleAuthView(APIView):
    def post(self, request):
        code = request.data.get("code")

        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": "http://127.0.0.1:8000/api/v1/users/google/callback/",
            "grant_type": "authorization_code",
        }
        token_resp = requests.post(token_url, data=data).json()
        access_token = token_resp.get("access_token")

        user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        user_info = requests.get(user_info_url, headers={"Authorization": f"Bearer {access_token}"}).json()

        email = user_info["email"]
        first_name = user_info.get("given_name", "")
        last_name = user_info.get("family_name", "")

        user, _ = CustomUser.objects.get_or_create(email=email, defaults={
            "username": email,
            "first_name": first_name,
            "last_name": last_name,
        })

        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
        })