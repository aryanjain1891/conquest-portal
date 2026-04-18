from rest_framework import generics, permissions
from .models import MeetingSlot, MeetingRequest, GlobalEvent, BookingPortal
from .serializers import MeetingSlotSerializer, MeetingRequestSerializer, GlobalEventSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from rest_framework import status
from .utils import create_google_meet_event


def portal_state_view(request):
    portal_state = BookingPortal.objects.first()
    if portal_state:
        return JsonResponse({'is_active': portal_state.is_active})
    return JsonResponse({'is_active': False})


# The below use generics.ListCreateAPIView does the following according to the request method,
# if request.method is POST--> creates a new object of that model.
# if request.method is GET--> shows the list of existing objects in the model.
class MeetingSlotCreate(generics.ListCreateAPIView):
    serializer_class = MeetingSlotSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Below code overrides the perform_create method of DRF and creates a slot associated to the current user.
    def perform_create(self, serializer):
        serializer.save(user=self.request.user.profile)
    
    # Below code also overrites the get_queryset method from ListCreateAPIView
    def get_queryset(self):
        user = self.request.user
        queryset = MeetingSlot.objects.filter(user=user.profile)
        return queryset


# Below generics.RetrieveUpdateDestroyAPIView is similar to above since it,
# handel GET request to fetch a single instance of the model.
# handel PUT and PATCH request to update a single object of the model.
# handel DELETE request to delete a single object of the model.
class MeetingSlotDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MeetingSlotSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = MeetingSlot.objects.filter(user=user.profile)
        return queryset


class MeetingRequestCreate(generics.ListCreateAPIView):
    serializer_class = MeetingRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        requester = self.request.user.profile
        requested = serializer.validated_data.get('requested')
        slot_start_time = serializer.validated_data.get('slot_start_time')
        slot_end_time = serializer.validated_data.get('slot_end_time')
        slot = serializer.validated_data.get('slot')

        if slot is not None and MeetingRequest.objects.filter(requester=requester, requested=requested, slot=slot).exists():
            raise ValidationError(f"You have already requested a meeting with {requested.name} in this slot.")
        
        # Below happens only when request has been made by the cme user to startup.
        if slot is None:
            if slot_start_time is None or slot_end_time is None:
                raise ValidationError("Either slot or both slot_start_time and slot_end_time must be provided.")
            
            # Check for clashing meetings
            clashing_meetings = MeetingSlot.objects.filter(
                user=requester,
                start_time__lt=slot_end_time,
                end_time__gt=slot_start_time,
                free=False
            )
            
            if clashing_meetings.exists():
                raise ValidationError("You have another meeting scheduled for this time.")
            
            # Check for free slots
            free_slots = MeetingSlot.objects.filter(
                user=requester,
                start_time__lt=slot_end_time,
                end_time__gt=slot_start_time,
                free=True
            )

            if free_slots.exists():
                # Update the first free slot found
                free_slot = free_slots.first()
                
                free_slot.save()
                slot = free_slot
            else:
                # Create a new slot if no clashes or free slots
                slot = MeetingSlot.objects.create(
                    user=requester,
                    start_time=slot_start_time,
                    end_time=slot_end_time,
                    free=True
                )
            # Below is to ensure that when flow2 happen when cme requests to startup then there is no need for cel approval.
            # But if this flow is followed then meet link must be generated automatically.
            serializer.save(requester=requester, slot=slot, cel_approved=True)
        else:
            serializer.save(requester=requester, slot=slot)

    def get_queryset(self):
        user = self.request.user
        return MeetingRequest.objects.filter(requested=user.profile)


class MeetingRequestDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MeetingRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    def perform_update(self, serializer):
        instance = serializer.save()

        # Check if status has been updated to rejected
        if instance.status == 'rejected':
            if instance.slot:
                instance.slot.delete()
                instance.slot = None
                instance.save()
        
        # Check if status has been updated to accepted
        if instance.status == 'accepted':
            if instance.slot:
                instance.slot.free = False
                instance.slot.save()
                instance.save()
                if not instance.meet_link:
                    # attendees_emails = [instance.requester.google_email, instance.requested.google_email]
                    instance.meet_link = create_google_meet_event(
                        f"Meeting between {instance.requester.name} and {instance.requested.name}",
                        instance.slot.start_time,
                        instance.slot.end_time)
                    instance.save()


    def get_queryset(self):
        user = self.request.user
        queryset = MeetingRequest.objects.filter(requested=user.profile)
        return queryset

class GlobalEventCreate(generics.ListCreateAPIView):
    queryset = GlobalEvent.objects.all()
    serializer_class = GlobalEventSerializer
    permission_classes = [permissions.IsAuthenticated]

class GlobalEventDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = GlobalEvent.objects.all()
    serializer_class = GlobalEventSerializer
    permission_classes = [permissions.IsAuthenticated]

class UserMeetingSlotsView(generics.ListAPIView):
    serializer_class = MeetingSlotSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return MeetingSlot.objects.filter(user__id=user_id, free=True)

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset.exists():
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response({"detail": "No meeting slots found for this user."}, status=status.HTTP_404_NOT_FOUND)



# Below decorators(@api_vies) are from DRF to define that these functions are API endpoints and is used in specific request method.
# Upcoming_meetings also includes ongoing meetings because we used gte instead of gt.
# Below both functions is for startups when they click
#Below are the meetings which has been send by other user to current user.ie. below are the received requestes

@api_view(['GET'])
def upcoming_meetings(request):
    user = request.user.profile
    
    # Fetch accepted and CEL-approved meeting requests
    meetings_requested = MeetingRequest.objects.filter(
        slot__start_time__gte=timezone.now(),
        status='accepted',
        cel_approved=True,
        requested=user
    )
    meetings_requester = MeetingRequest.objects.filter(
        slot__start_time__gte=timezone.now(),
        status='accepted',
        cel_approved=True,
        requester=user
    )
    meetings = meetings_requester | meetings_requested

    # Fetch global events after the current time
    global_events = GlobalEvent.objects.filter(slot_start_time__gte=timezone.now())

    # Serialize meeting requests and global events
    meeting_serializer = MeetingRequestSerializer(meetings, many=True)
    event_serializer = GlobalEventSerializer(global_events, many=True)

    # Combine the serialized data
    response_data = {
        'meetings': meeting_serializer.data,
        'global_events': event_serializer.data,
    }

    return Response(response_data)


@api_view(['GET'])
def past_meetings(request):
    user = request.user.profile
    meetings_requested = MeetingRequest.objects.filter(
        slot__start_time__lt=timezone.now(),
        status='accepted',
        cel_approved=True,
        requested=user
    )
    meetings_requester = MeetingRequest.objects.filter(
        slot__start_time__lt=timezone.now(),
        cel_approved=True,
        status='accepted',
        requester=user
    )
    meetings = meetings_requester | meetings_requested

    # Fetch global events after the current time
    global_events = GlobalEvent.objects.filter(slot_start_time__lt=timezone.now())

    # Serialize meeting requests and global events
    meeting_serializer = MeetingRequestSerializer(meetings, many=True)
    event_serializer = GlobalEventSerializer(global_events, many=True)

    # Combine the serialized data
    response_data = {
        'meetings': meeting_serializer.data,
        'global_events': event_serializer.data,
    }

    return Response(response_data)

@api_view(['GET'])
def pending_meetings(request):
    user = request.user.profile
    meetings = MeetingRequest.objects.filter(slot__start_time__gte=timezone.now(), status='pending', cel_approved=True, requested=user)
    serializer = MeetingRequestSerializer(meetings, many=True)
    return Response(serializer.data)

# Below is for if front team want the meetings in single url to decrease the time to fetch the data.
# @front can access the meet start time by object.slot.start_time and status by object.status
@api_view(['GET'])
def all_meetings(request):
    user = request.user.profile
    meetings = MeetingRequest.objects.filter(requested=user)
    serializer = MeetingRequestSerializer(meetings, many=True)
    return Response(serializer.data)

# Below are the sent requests by the current user
@api_view(['GET'])
def requested_meetings(request):
    user = request.user.profile
    meetings = MeetingRequest.objects.filter(requester=user)
    serializer = MeetingRequestSerializer(meetings, many=True)
    return Response(serializer.data)
