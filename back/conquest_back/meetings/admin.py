from django.contrib import admin
from .models import MeetingSlot, MeetingRequest, GlobalEvent, BookingPortal
from import_export.admin import ImportExportModelAdmin,ExportActionMixin
from .resources import MeetingRequestResource
from nested_inline.admin import NestedModelAdmin

class MeetingSlotAdmin(admin.ModelAdmin):
    model=MeetingSlot
    list_display = ('user', 'start_time', 'end_time')
    list_filter = ('user',)
admin.site.register(MeetingSlot,MeetingSlotAdmin)


class MeetingRequestAdmin(NestedModelAdmin,ImportExportModelAdmin,ExportActionMixin):
    model=MeetingRequest
    resource_class=MeetingRequestResource
    list_display = ('requester', 'requested', 'slot', 'status')
    list_filter = ('status',)
    #search_fields = ('requester__name', 'requested__name')

admin.site.register(MeetingRequest,MeetingRequestAdmin)


class GlobalEventAdmin(admin.ModelAdmin):
    model=GlobalEvent
    list_display = ('name', 'slot_start_time','slot_end_time')
    
admin.site.register(GlobalEvent,GlobalEventAdmin)
admin.site.register(BookingPortal)
