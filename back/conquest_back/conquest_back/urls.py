from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
import users.urls
from django.http import JsonResponse

def trigger_error(request):
    division_by_zero = 1 / 0

def health_view(request):
    return JsonResponse({'status': 'OK'})


urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('api/users/',include('users.urls')),
    path('api/forms/',include('forms.urls')),
    path('api/meetings/', include('meetings.urls')),
    path('api/staff/', include('staff.urls')),
    path('api/v1/health', health_view ),
    path('api/sentry-debug/', trigger_error),
]
#+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)+static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)
