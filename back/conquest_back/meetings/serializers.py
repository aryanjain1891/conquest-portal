from rest_framework import serializers
from .models import MeetingSlot, MeetingRequest, GlobalEvent
from datetime import datetime
from django.utils import timezone
import pytz

# class MeetingSlotSerializer(serializers.ModelSerializer):
#     start_time = serializers.SerializerMethodField()
#     end_time = serializers.SerializerMethodField()
#     user_name = serializers.CharField(source='user.name', read_only=True)  # Corrected user field access

#     class Meta:
#         model = MeetingSlot
#         fields = ['id', 'user_name', 'start_time', 'end_time', 'free']

#     def get_start_time(self, obj):
#         if obj.start_time.tzinfo is None:
#             obj.start_time = obj.start_time.replace(tzinfo=pytz.UTC)
#         return int(timezone.localtime(obj.start_time).timestamp())

#     def get_end_time(self, obj):
#         if obj.end_time.tzinfo is None:
#             obj.end_time = obj.end_time.replace(tzinfo=pytz.UTC)
#         return int(timezone.localtime(obj.end_time).timestamp())

#     def to_internal_value(self, data):
#         internal_value = super().to_internal_value(data)
#         if 'start_time' in data:
#             internal_value['start_time'] = datetime.fromtimestamp(int(data['start_time']), pytz.UTC)
#         if 'end_time' in data:
#             internal_value['end_time'] = datetime.fromtimestamp(int(data['end_time']), pytz.UTC)
#         return internal_value


class MeetingSlotSerializer(serializers.ModelSerializer):
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()
    user_name = serializers.CharField(source='user.name', read_only=True)  # Corrected user field access

    class Meta:
        model = MeetingSlot
        fields = ['id', 'user_name', 'start_time', 'end_time', 'free']

    def get_start_time(self, obj):
        return int(obj.start_time.timestamp())  # No need to convert to local time

    def get_end_time(self, obj):
        return int(obj.end_time.timestamp())  # No need to convert to local time
    
    def to_internal_value(self, data):
        internal_value = super().to_internal_value(data)
        if 'start_time' in data:
            internal_value['start_time'] = datetime.fromtimestamp(int(data['start_time']), pytz.UTC)
        if 'end_time' in data:
            internal_value['end_time'] = datetime.fromtimestamp(int(data['end_time']), pytz.UTC)
        return internal_value


class MeetingRequestSerializer(serializers.ModelSerializer):
    requester_name = serializers.CharField(source='requester.name', read_only=True)
    requested_name = serializers.CharField(source='requested.name', read_only=True)
    requester_email = serializers.CharField(source='requester.google_email', read_only=True)
    requested_email = serializers.CharField(source='requested.google_email', read_only=True)
    requester_logo = serializers.URLField(source='requester.profile_logo', read_only=True)
    requested_logo = serializers.URLField(source='requested.profile_logo', read_only=True)
    slot_start_time = serializers.SerializerMethodField()
    slot_end_time = serializers.SerializerMethodField()

    class Meta:
        model = MeetingRequest
        fields = [
            'id', 'status', 'slot', 'meet_link', 'requester', 'requested',
            'requester_name', 'requested_name', 'requester_email', 'requested_email',
            'requester_logo', 'requested_logo', 'slot_start_time', 'slot_end_time', 'cel_approved'
        ]

    def get_slot_start_time(self, obj):
        if obj.slot and obj.slot.start_time.tzinfo is not None:
            return int(timezone.localtime(obj.slot.start_time).timestamp())
        elif obj.slot:
            return int(obj.slot.start_time.replace(tzinfo=pytz.UTC).timestamp())
        return None

    def get_slot_end_time(self, obj):
        if obj.slot and obj.slot.end_time.tzinfo is not None:
            return int(timezone.localtime(obj.slot.end_time).timestamp())
        elif obj.slot:
            return int(obj.slot.end_time.replace(tzinfo=pytz.UTC).timestamp())
        return None

    def to_internal_value(self, data):
        internal_value = super().to_internal_value(data)
        if 'slot_start_time' in data:
            internal_value['slot_start_time'] = datetime.fromtimestamp(int(data['slot_start_time']), pytz.UTC)
        if 'slot_end_time' in data:
            internal_value['slot_end_time'] = datetime.fromtimestamp(int(data['slot_end_time']), pytz.UTC)
        return internal_value

    def validate(self, data):
        slot = data.get('slot')
        slot_start_time = data.get('slot_start_time')
        slot_end_time = data.get('slot_end_time')

        if slot is None and (slot_start_time is None or slot_end_time is None):
            raise serializers.ValidationError("Either slot or both slot_start_time and slot_end_time must be provided.")
        
        return data


class GlobalEventSerializer(serializers.ModelSerializer):
    slot_start_time = serializers.SerializerMethodField()
    slot_end_time = serializers.SerializerMethodField()

    class Meta:
        model = GlobalEvent
        fields = ['id', 'name', 'description', 'slot_start_time', 'slot_end_time', 'meet_link', 'recording']
    
    def get_slot_start_time(self, obj):
        return int(obj.slot_start_time.timestamp())

    def get_slot_end_time(self, obj):
        return int(obj.slot_end_time.timestamp())
    
    def to_internal_value(self, data):
        internal_value = super().to_internal_value(data)
        if 'slot_start_time' in data:
            internal_value['slot_start_time'] = datetime.fromtimestamp(int(data['slot_start_time']), pytz.UTC)
        if 'slot_end_time' in data:
            internal_value['slot_end_time'] = datetime.fromtimestamp(int(data['slot_end_time']), pytz.UTC)
        return internal_value
