from django.urls import path
from .views import (
    MeetingSlotCreate, MeetingSlotDetail,
    MeetingRequestCreate, MeetingRequestDetail,
    GlobalEventCreate, GlobalEventDetail, UserMeetingSlotsView,
    upcoming_meetings, past_meetings,   
    pending_meetings, all_meetings, requested_meetings, portal_state_view
)

urlpatterns = [
    path('portal_state/', portal_state_view, name='portal-state'),
    path('slots/', MeetingSlotCreate.as_view(), name='meeting-slot-create'),
    path('slots/<int:pk>/', MeetingSlotDetail.as_view(), name='meeting-slot-detail'),
    path('user/<int:user_id>/meeting-slots/', UserMeetingSlotsView.as_view(), name='user-meeting-slots'),
    path('requests/', MeetingRequestCreate.as_view(), name='meeting-request-create'), # this will work same as (all_meetings/)
    path('requests/<int:pk>/', MeetingRequestDetail.as_view(), name='meeting-request-detail'),
    path('event/', GlobalEventCreate.as_view(), name='global-event-create'),
    path('event/<int:pk>/', GlobalEventDetail.as_view(), name='global-event-detail'),
    path('meetings/upcoming/', upcoming_meetings, name='upcoming-meetings'),
    path('meetings/past/', past_meetings, name='past-meetings'),
    path('meetings/pending/', pending_meetings, name='pending-meetings'),
    path('all_meetings/', all_meetings, name='all-meetings'),
    path('requested_meetings/', requested_meetings, name='all-requested-meetings')
]

"""
Endpoints:

/slots/
Method: POST
Header: Authorization: Bearer <access_token>
{
    "user": <user_profile_id>, @front, always send 1 here or 2 it doesn't matter because backend is extracting this data from token and overwrite the sent user.
    "start_time": "2024-06-05T10:00:00",
    "end_time": "2024-06-05T11:00:00"
}

/slots/<int:pk>/
Method: PUT or PATCH
Header: Authorization: Bearer <access_token>
{
    "user": <user_profile_id>, @front, send 1 here
    "start_time": "2024-06-05T10:00:00",
    "end_time": "2024-06-05T11:00:00"
}

/slots/
Method: GET
Header: Authorization: Bearer <access_toked>
Note: This will give the list of all the slots for this user in the header.

/requests/
Method: POST
Header: Authorization: Bearer <access_token>
{
    "requester": <requester_profile_id>,
    "requested": <requested_profile_id>,
    "slot": <meeting_slot_id>,
    "meet_link": "A URL" --> bhaiya se puchna hai ke ye kab generate karna hai
}

/requests/<int:pk>/
Method: PATCH
Header: Authorization: Bearer <access_token>
Note: This is to accept the request of meeting from startup to cme user.
{
    "status": "accepted",
}

/meetings/meetings/upcoming/
Method: GET
Header: Authorization: Bearer <access_token>
Note: it only gives the meetings who has status:"accept"


/meetings/meetings/past/
Method: GET
Header: Authorization: Bearer <access_token>
Note: This also gives the meetings who has status:"accept" although it can be changed if someone wants.


/meetings/meetings/pending/
Method: GET
Header: Authorization: Bearer <access_token>
Note: it only gives the meetings who has status:"pending" and whose meetings slot has not been past.


"""

"""
I will create a different model for the feedback and ratings if they are captured after the meeting is ended.
"""
