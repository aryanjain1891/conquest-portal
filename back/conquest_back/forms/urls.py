from django.urls import path
from .views import *

urlpatterns = [
    path("list/",GetForms.as_view(),name="get-forms"),
    path("<int:pk>/questions/",GetFormQuestions,name="get-questions"),
    path("<int:pk>/answers/",AddAnswers,name="post-questions"),
    path("send-email/", send_resource_email, name="send-resource-email")
]
