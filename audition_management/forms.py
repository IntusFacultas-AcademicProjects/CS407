from django import forms
from django.contrib.auth.models import User
from audition_management.models import (
    PastWork, Role, PerformanceEvent, Tag, AuditionAccount)
from bootstrap3_datetime.widgets import DateTimePicker
from django_select2.forms import (
    Select2Widget
)


class SettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    # TODO validate better
    def clean_username(self):
        data = self.cleaned_data['username']
        data = data.replace("'", "")
        data = data.replace('"', "")
        data = data.replace('\\', "")
        return data

    def clean_first_name(self):
        data = self.cleaned_data['first_name']
        data = data.replace("'", "")
        data = data.replace('"', "")
        data = data.replace('\\', "")
        return data

    def clean_last_name(self):
        data = self.cleaned_data['last_name']
        data = data.replace("'", "")
        data = data.replace('"', "")
        data = data.replace('\\', "")
        return data

    def clean_email(self):
        data = self.cleaned_data['email']
        data = data.replace("'", "")
        data = data.replace('"', "")
        data = data.replace('\\', "")
        return data


class AuditionSettingsForm(forms.ModelForm):
    class Meta:
        model = AuditionAccount
        fields = ('gender', 'age', 'ethnicity', 'location')

    def clean_location(self):
        data = self.cleaned_data['location']
        data = data.replace("'", "")
        data = data.replace('"', "")
        data = data.replace('\\', "")
        return data

class CastingSettingsForm(forms.ModelForm):
    class Meta:
        model = CastingAccount
        fields = ('location','phone')

    def clean_location(self):
        data = self.cleaned_data['location']
        data = data.replace("'", "")
        data = data.replace('"', "")
        data = data.replace('\\', "")
        return data


class PortfolioForm(forms.ModelForm):
    class Meta:
        model = PastWork
        fields = ['name']

    def clean_name(self):
        data = self.cleaned_data['name']
        data = data.replace("'", "")
        data = data.replace('"', "")
        data = data.replace('\\', "")
        return data


class RoleCreationForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ('name', 'description', 'domain', 'studio_address')
        widgets = {
            'domain': Select2Widget,
        }

    def clean_name(self):
        data = self.cleaned_data['name']
        data = data.replace("'", "")
        data = data.replace('"', "")
        data = data.replace('\\', "")
        return data

    def clean_description(self):
        data = self.cleaned_data['description']
        data = data.replace("'", "")
        data = data.replace('"', "")
        data = data.replace('\\', "")
        return data

    def clean_studio_address(self):
        data = self.cleaned_data['studio_address']
        data = data.replace("'", "")
        data = data.replace('"', "")
        data = data.replace('\\', "")
        return data


class EditRoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ('name', 'description', 'domain', 'studio_address', 'status')
        widgets = {
            'domain': Select2Widget,
            'status': Select2Widget
        }

    def clean_name(self):
        data = self.cleaned_data['name']
        data = data.replace("'", "")
        data = data.replace('"', "")
        data = data.replace('\\', "")
        return data

    def clean_description(self):
        data = self.cleaned_data['description']
        data = data.replace("'", "")
        data = data.replace('"', "")
        data = data.replace('\\', "")
        return data

    def clean_studio_address(self):
        data = self.cleaned_data['studio_address']
        data = data.replace("'", "")
        data = data.replace('"', "")
        data = data.replace('\\', "")
        return data


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name']

    def clean_name(self):
        data = self.cleaned_data['name']
        data = data.replace("'", "")
        data = data.replace('"', "")
        data = data.replace('\\', "")
        return data


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

    def clean_name(self):
        data = self.cleaned_data['name']
        data = data.replace("'", "")
        data = data.replace('"', "")
        data = data.replace('\\', "")
        return data


PortfolioFormSet = forms.inlineformset_factory(
    AuditionAccount, PastWork, extra=1, form=PortfolioForm, can_delete=True)
ProfileTagFormSet = forms.inlineformset_factory(
    AuditionAccount, Tag, extra=1, form=TagForm, can_delete=True)
TagFormSet = forms.inlineformset_factory(
    Role, Tag, extra=1, form=TagForm, can_delete=True)
EventFormSet = forms.inlineformset_factory(
    Role, PerformanceEvent, extra=1, form=EventForm, can_delete=True)
