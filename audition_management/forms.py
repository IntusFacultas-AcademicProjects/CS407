from django import forms
from django.contrib.auth.models import User
from audition_management.models import Role, PerformanceEvent, Tag
from audition_management.models import CastingAccount
from bootstrap3_datetime.widgets import DateTimePicker
from django_select2.forms import (
    HeavySelect2MultipleWidget, HeavySelect2Widget, ModelSelect2MultipleWidget,
    ModelSelect2TagWidget, ModelSelect2Widget, Select2MultipleWidget,
    Select2Widget
)


class SettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    # TODO validate better


class RoleCreationForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ('name', 'description', 'domain', 'studio_address')
        widgets = {
            'domain': Select2Widget,
        }


class EditRoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ('name', 'description', 'domain', 'studio_address', 'status')
        widgets = {
            'domain': Select2Widget,
            'status': Select2Widget
        }


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name']


class EventForm(forms.ModelForm):
    class Meta:
        model = PerformanceEvent
        fields = ['name', 'date']
        widgets = {
            'date': DateTimePicker(options={
                "format": "YYYY-MM-DD HH:mm",
                "icons": {
                    "date": "glyphicon glyphicon-time",
                    "up": "fa fa-arrow-up",
                    "down": "fa fa-arrow-down"
                }
            })
        }


TagFormSet = forms.inlineformset_factory(
    Role, Tag, extra=1, form=TagForm, can_delete=True)
EventFormSet = forms.inlineformset_factory(
    Role, PerformanceEvent, extra=1, form=EventForm, can_delete=True)
