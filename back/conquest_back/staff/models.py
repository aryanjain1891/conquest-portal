from django.db import models
from users.models import *
# Create your models here.

class Announcement(models.Model):
    roles = models.CharField(max_length=len(ALL_ROLES)*30, default='Startup')
    message = models.TextField(max_length=1000, null=False)
    attachment = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.message[:50]
    
    def get_roles_display(self):
        return ', '.join(self.roles.split(',')) if self.roles else 'None'
    
class Notification(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=False)
    message = models.CharField(max_length=1000)
    read = models.BooleanField(default=False)
    attachment = models.URLField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Notification for {self.user} - {self.message[:20]}'
    
