from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from users.models import User, UserProfile, Startup,Connection
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import *
from users.serializers import ConnectionSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
import random
import requests
from rest_framework.permissions import AllowAny
from rest_framework.authentication import authenticate
import datetime
from django.db.models import Q

class GetNotifications(APIView):
    permission_class = [IsAuthenticated]

    def get(self, request):
        try:
            user_profile = request.user.profile
        except:
            return Response({"error":"user has no user profile"},
                            status=404)
        
        notifications = Notification.objects.filter(user=user_profile)
        unread_count=notifications.filter(read=False).count()

        serialized_notifications=NotificationSerializer(notifications, many=True).data
        # print(serialized_notifications[0].message)
        return Response({
            "notifications": serialized_notifications,
            "unread_count": unread_count
        }, status=200)