from django import forms
from django.contrib.auth.models import User
from audition_management.models import Skill, PastWork, Role, PerformanceEvent, Tag, AuditionAccount
from bootstrap3_datetime.widgets import DateTimePicker
from django_select2.forms import (
    Select2Widget
)


class SettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    # TODO validate better

class SkillsForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name']

class PortfolioForm(forms.ModelForm):
    class Meta:
        model = PastWork
        fields = ['name']


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

SkillsFormSet = forms.inlineformset_factory(
    AuditionAccount, Skill, extra=1, form=SkillsForm, can_delete=True)
PortfolioFormSet = forms.inlineformset_factory(
    AuditionAccount, PastWork, extra=1, form=PortfolioForm, can_delete=True)

TagFormSet = forms.inlineformset_factory(
    Role, Tag, extra=1, form=TagForm, can_delete=True)
EventFormSet = forms.inlineformset_factory(
    Role, PerformanceEvent, extra=1, form=EventForm, can_delete=True)
