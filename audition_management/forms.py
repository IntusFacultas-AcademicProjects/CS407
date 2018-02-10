from django import forms
from django.contrib.auth.models import User

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
