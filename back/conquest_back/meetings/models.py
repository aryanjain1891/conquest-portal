from django.db import models
from django.contrib.auth.models import User
from users.models import UserProfile
from django.core.validators import MaxValueValidator, MinValueValidator
import pytz
from django.utils import timezone


# The free time that the c/m/e user or startup user have.
class MeetingSlot(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    start_time = models.DateTimeField(default=timezone.now)  # Updated
    end_time = models.DateTimeField(default=timezone.now)  # Updated
    free = models.BooleanField(default=True, null=True, blank=True)

    def __str__(self):
        # Convert times to local timezone
        local_timezone = pytz.timezone('Asia/Kolkata')  # Replace with your local timezone
        start_time_local = self.start_time.astimezone(local_timezone)
        end_time_local = self.end_time.astimezone(local_timezone)
        
        # Format the times
        start_time_str = start_time_local.strftime('%Y-%m-%d %H:%M')
        end_time_str = end_time_local.strftime('%Y-%m-%d %H:%M')
        
        return f"{self.user.name} - {start_time_str} to {end_time_str}"

class MeetingRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ]

    requester = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='sent_requests')
    requested = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='received_requests')
    slot = models.ForeignKey(MeetingSlot, on_delete=models.SET_NULL, null=True, blank=True)
    slot_start_time = models.DateTimeField(null=True, blank=True)
    slot_end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    meet_link = models.URLField(blank=True, null=True)
    recording = models.URLField(blank=True, null=True)
    minutes_of_meet = models.TextField(blank=True, null=True)
    requester_feedback_score = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        blank=True,
        null=True
    )
    requested_feedback_score = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        blank=True,
        null=True
    )
    cel_approved=models.BooleanField(default=False)


    @property
    def type(self):
        return self.requester.role+"/"+self.requested.role

    def save(self, *args, **kwargs):
        # Make sure slot_start_time and slot_end_time are aware datetimes
        if self.slot_start_time and self.slot_start_time.tzinfo is None:
            self.slot_start_time = self.slot_start_time.replace(tzinfo=pytz.UTC)
        if self.slot_end_time and self.slot_end_time.tzinfo is None:
            self.slot_end_time = self.slot_end_time.replace(tzinfo=pytz.UTC)

        
        # # Check if the slot is being assigned and status is pending
        # if self.slot and self.status == 'pending':
        #     self.slot.free = False
        #     self.slot.save()

        # Check if the status is changing to rejected
        if self.pk is not None:
            old_status = MeetingRequest.objects.get(pk=self.pk).status
            if old_status != 'rejected' and self.status == 'rejected':
                if self.slot:
                    self.slot.delete()
                    self.slot = None
        
        # Check if the status is changing to accepted
        if self.pk is not None:
            old_status = MeetingRequest.objects.get(pk=self.pk).status
            if old_status != 'accepted' and self.status == 'accepted':
                if self.slot:
                    self.slot.free = False
                    self.slot.save()

        if self.pk is not None and self.requester.role == 'Startup':
            old_approval = MeetingRequest.objects.get(pk=self.pk).cel_approved
            if old_approval != True and self.cel_approved == True:
                self.status = 'accepted'
                self.slot.free = False
                self.slot.save()

        super(MeetingRequest, self).save(*args, **kwargs)

    def __str__(self):
        return f'Request from {self.requester} to {self.requested}'


class GlobalEvent(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    slot_start_time = models.DateTimeField(default=timezone.now)
    slot_end_time = models.DateTimeField(default=timezone.now)
    meet_link = models.URLField(blank=True, null=True)
    recording = models.URLField(blank=True, null=True)
    
    def __str__(self):
        # Convert times to local timezone
        local_timezone = pytz.timezone('Asia/Kolkata')  # Replace with your local timezone
        start_time_local = self.slot_start_time.astimezone(local_timezone)
        end_time_local = self.slot_end_time.astimezone(local_timezone)
        
        # Format the times
        start_time_str = start_time_local.strftime('%Y-%m-%d %H:%M')
        end_time_str = end_time_local.strftime('%Y-%m-%d %H:%M')
        
        return f"{self.name} - {start_time_str} to {end_time_str}"


class BookingPortal(models.Model):
    is_active = models.BooleanField(default=False)
    
    def __str__(self):
        return "Scheduled Booking is Active" if self.is_active else "Scheduled Booking is Inactive"
