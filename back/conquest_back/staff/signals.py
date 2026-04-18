from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Announcement, Notification
from users.models import UserProfile

@receiver(post_save, sender=Announcement)
def notify_users(sender, instance, created, **kwargs):
    if created:  # Only notify when an announcement is created
        roles = instance.roles.split(',')
        users_to_notify = UserProfile.objects.filter(role__in=roles)
        
        for user_profile in users_to_notify:
            Notification.objects.create(
                user=user_profile,
                message=instance.message,
                attachment=instance.attachment
            )
