from import_export import resources,fields,widgets

from .models import *

class MeetingRequestResource(resources.ModelResource):

    type=fields.Field('type',column_name="Meeting Type")
    class Meta:
        model=MeetingRequest
        fields=("id","type","requester__name","requested__name","slot__start_time","slot__end_time","cel_approved","status","meet_link","recording")
        import_id_fields=("id",)

    def import_field(self, field, obj, data, is_m2m=False,**kwargs):
        """
        Overriding import_field method to exclude specific fields during import.
        """
        if field.column_name == 'Meeting Type':
            # Skip this field during import
            return None
        return super().import_field(field, obj, data, is_m2m,**kwargs)