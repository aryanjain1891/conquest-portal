from rest_framework import serializers
from .models import *
from users.serializers import UserProfileSerializer

class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['message', 'read', 'attachment', 'timestamp']