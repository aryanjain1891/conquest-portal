from django.contrib import admin
from .models import Announcement, Notification
from .forms import AnnouncementAdminForm

class AnnouncementAdmin(admin.ModelAdmin):
    form = AnnouncementAdminForm
    list_display = ('message', 'get_roles_display', 'attachment')

    def save_model(self, request, obj, form, change):
        obj.roles = ','.join(form.cleaned_data['roles'])
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser and not request.user.is_staff:
            return ['roles', 'message', 'attachment']
        return []

    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_staff

admin.site.register(Announcement, AnnouncementAdmin)
admin.site.register(Notification)
