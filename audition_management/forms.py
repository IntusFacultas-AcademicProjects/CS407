from django import forms
from django.contrib.auth.models import User


class SettingsForm(forms.ModelForm):
    username = forms.CharField(max_length=30, required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254)
    password1 = forms.PasswordInput()
    password2 = forms.PasswordInput()

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1',
            'password2')

    # TODO validate better
from audition_management import models
from audition_management.models import CastingAccount


class RoleCreationForm(forms.ModelForm):
    name = forms.CharField(max_length=256, required=True)
    description = forms.CharField(max_length=512, required=True) #confirm
    domain = forms.ComboField("Role", choices=models.Role.DOMAIN_CHOICES)
    studio_address = forms.CharField(max_length=512, required=False)

    class Meta:
        model = User
        fields = ('name', 'description', 'domain', 'studio_address')
