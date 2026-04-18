from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType

@receiver(post_save, sender=User)
def assign_staff_permissions(sender, instance, created, **kwargs):
    if hasattr(instance, '_signal_processed') and instance._signal_processed:
        return
    
    instance._signal_processed = True

    if instance.is_staff:
        # Specify the permissions to assign to staff users
        staff_permissions = [
            'add_userprofile',    # Example: can add user profile
            'change_userprofile', # Example: can change user profile
            'delete_userprofile', # Example: can delete user profile
            'view_userprofile',   # Example: can view user profile
            'add_answer',    # Example: can add user profile
            'change_answer', # Example: can change user profile
            'delete_answer', # Example: can delete user profile
            'view_answer',   # Example: can view user profile
            'add_fileans',    # Example: can add user profile
            'change_fileans', # Example: can change user profile
            'delete_fileans', # Example: can delete user profile
            'view_fileans',
            'add_form',    # Example: can add user profile
            'change_form', # Example: can change user profile
            'delete_form', # Example: can delete user profile
            'view_form',   # Example: can view user profile
            'add_preference',    # Example: can add user profile
            'change_preference', # Example: can change user profile
            'delete_preference', # Example: can delete user profile
            'view_preference',
            'add_preferenceans',    # Example: can add user profile
            'change_preferenceans', # Example: can change user profile
            'delete_preferenceans', # Example: can delete user profile
            'view_preferenceans',
            'add_preferenceansmain',    # Example: can add user profile
            'change_preferenceansmain', # Example: can change user profile
            'delete_preferenceansmain', # Example: can delete user profile
            'view_preferenceansmain',
            'add_preferencequestion',    # Example: can add user profile
            'change_preferencequestion', # Example: can change user profile
            'delete_preferencequestion', # Example: can delete user profile
            'view_preferencequestion',
            'add_scoreans',    # Example: can add user profile
            'change_scoreans', # Example: can change user profile
            'delete_scoreans', # Example: can delete user profile
            'view_scoreans',
            'add_scoringquestion',    # Example: can add user profile
            'change_scoringquestion', # Example: can change user profile
            'delete_scoringquestion', # Example: can delete user profile
            'view_scoringquestion',
            'add_subjectiveans',    # Example: can add user profile
            'change_subjectiveans', # Example: can change user profile
            'delete_subjectiveans', # Example: can delete user profile
            'view_subjectiveans',
            'add_subjectivequestion',    # Example: can add user profile
            'change_subjectivequestion', # Example: can change user profile
            'delete_subjectivequestion', # Example: can delete user profile
            'view_subjectivequestion',
            'add_link',    # Example: can add user profile
            'change_link', # Example: can change user profile
            'delete_link', # Example: can delete user profile
            'view_link',   # Example: can view user profile
            'add_globalevent',    # Example: can add user profile
            'change_globalevent', # Example: can change user profile
            'delete_globalevent', # Example: can delete user profile
            'view_globalevent',   # Example: can view user profile
            'add_meeting',    # Example: can add user profile
            'change_meeting', # Example: can change user profile
            'delete_meeting', # Example: can delete user profile
            'view_meeting',   # Example: can view user profile
            'add_meetingrequest',    # Example: can add user profile
            'change_meetingrequest', # Example: can change user profile
            'delete_meetingrequest', # Example: can delete user profile
            'view_meetingrequest',   # Example: can view user profile
            'add_meetingslot',    # Example: can add user profile
            'change_meetingslot', # Example: can change user profile
            'delete_meetingslot', # Example: can delete user profile
            'view_meetingslot',   # Example: can view user profile
            'add_announcement',    # Example: can add user profile
            'change_announcement', # Example: can change user profile
            'delete_announcement', # Example: can delete user profile
            'view_announcement',   # Example: can view user profile
            'add_notification',    # Example: can add user profile
            'change_notification', # Example: can change user profile
            'delete_notification', # Example: can delete user profile
            'view_notification',   # Example: can view user profile
            'add_startup',    # Example: can add user profile
            'change_startup', # Example: can change user profile
            'delete_startup', # Example: can delete user profile
            'view_startup',
            'add_user',    # Example: can add user profile
            'change_user', # Example: can change user profile
            'delete_user', # Example: can delete user profile
            'view_user',
            'add_connection',    # Example: can add user profile
            'change_connection', # Example: can change user profile
            'delete_connection', # Example: can delete user profile
            'view_connection',
            
        ]

        print("running here")
        # Get the Permission objects
        permissions = Permission.objects.filter(codename__in=staff_permissions)
        print(permissions)
        
        # Assign the permissions to the user
        print(instance.user_permissions)
        instance.user_permissions.set(permissions)
        print(instance.user_permissions)
    else:
        # Remove permissions if the user is no longer staff
        instance.user_permissions.clear()

    # Ensure the instance is saved
    instance.save(update_fields=[])

    instance._signal_processed = False
