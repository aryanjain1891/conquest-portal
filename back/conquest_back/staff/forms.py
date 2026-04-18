from django import forms
from .models import Announcement
from users.models import ALL_ROLES
class AnnouncementAdminForm(forms.ModelForm):

    roles = forms.MultipleChoiceField(choices=ALL_ROLES, widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Announcement
        fields = ['roles', 'message', 'attachment']