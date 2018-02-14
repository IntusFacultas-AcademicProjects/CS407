from django import forms
from django.contrib.auth.models import User
from audition_management.models import Role
from audition_management.models import CastingAccount
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
