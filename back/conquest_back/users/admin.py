from django.contrib import admin
from .models import  Startup, UserProfile,Connection,StartUpMember,InterestCapture
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.core.exceptions import PermissionDenied

# Register your models here.

admin.site.register(Startup)
admin.site.register(StartUpMember)
class ConnectionAdmin(admin.ModelAdmin):
    model=Connection
    fields=('from_user',"to_user","approved",'accepted')
    list_display=('from_user',"to_user","approved",'accepted')
    list_editable=("approved",'accepted')

admin.site.register(Connection,ConnectionAdmin)



class FromConnectionInline(admin.TabularInline):
    model = Connection
    fk_name = 'from_user'
    extra = 0

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(from_user=self.parent_model_instance)

    def get_formset(self, request, obj=None, **kwargs):
        self.parent_model_instance = obj
        return super().get_formset(request, obj, **kwargs)

class ToConnectionInline(admin.TabularInline):
    model = Connection
    fk_name = 'to_user'
    extra = 0

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(to_user=self.parent_model_instance)

    def get_formset(self, request, obj=None, **kwargs):
        self.parent_model_instance = obj
        return super().get_formset(request, obj, **kwargs)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'profile_logo', 'google_email', 'google_user_id')
    list_filter=('role',)
    search_fields=('name',)
    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:  # Check if the logged-in user is not a superuser
            return ('user', 'profile_logo', 'google_email', 'google_user_id')
        return super(UserProfileAdmin, self).get_readonly_fields(request, obj)
    
    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.is_staff
    
    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_staff
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_staff
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_staff
    
    inlines = [ToConnectionInline, FromConnectionInline]

admin.site.register(UserProfile, UserProfileAdmin)

class UserAdmin(BaseUserAdmin):
    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser and obj.is_superuser:
            raise PermissionDenied("Staff users cannot create or modify a superuser.")
        super().save_model(request, obj, form, change)
        
    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return self.readonly_fields + ('is_superuser',)
        return self.readonly_fields

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

class InterestCaptureAdmin(admin.ModelAdmin):
    model = InterestCapture
    list_display = ('from_startup', 'get_target', 'interest_captured')
    list_filter = ('interest_captured',)

    def get_target(self, obj):
        if obj.for_consultant:
            return f'{obj.for_consultant.name}--consultant'
        elif obj.for_resource:
            return f'{obj.for_resource.user.username}--resource'
        return 'Unknown'
    get_target.short_description = 'Target'

admin.site.register(InterestCapture, InterestCaptureAdmin)
