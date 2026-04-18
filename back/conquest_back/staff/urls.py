from django.urls import path, include
from . import views as staff_views

urlpatterns=[
    path('notifications/', staff_views.GetNotifications.as_view(), name='get-notification'),
]