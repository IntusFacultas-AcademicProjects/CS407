from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.views import View
from audition_management import models
from audition_management.forms import SettingsForm


class DashboardView(View):

    @staticmethod
    def handle_request(request):
        if request.GET:
            return DashboardView.get(request)

    @staticmethod
    def get(request):
        roles = models.Role.objects.all()
        dictionaries = [obj.as_dict() for obj in roles]
        return render(request, 'audition_management/dashboard.html', {
            "roles": dictionaries
        })
from django.contrib import messages
# Create your views here.
from audition_management import models
from audition_management.forms import RoleCreationForm


class SettingsView(View):

    @staticmethod
    def handle_request(request):
        if request.GET:
            return SettingsView.get(request)
        else:
            return SettingsView.post(request)

    @staticmethod
    def get_user(current_user):
        user = models.AuditionAccount.objects.get(pk=current_user.id)
        if user is None:
            user = models.CastingAccount.objects.get(pk=current_user.id)
        return user

    def get(self, request):
        if not request.user.is_authenticated():
            return HttpResponseForbidden("403 Forbidden , you aren't logged in")
        user = self.get_user(request.user)
        form = SettingsForm(initial={
            'username': user.profile.username,
            'first_name': user.profile.first_name,
            'last_name': user.profile.last_name,
            'email': user.profile.email
        })
        return render(request, 'audition_management/settings.html', {
            "user": user.as_dict(),
            'form': form
        })

    def post(self, request):
        if not request.user.is_authenticated():
            return HttpResponseForbidden("403 Forbidden , you aren't logged in")
        user = self.get_user(request.user)
        form = SettingsForm(request.POST)
        if form.is_valid():
            user.profile.first_name = form.first_name
            user.profile.last_name = form.last_name
            user.profile.email = form.email
            user.profile.username = form.username
            user.profile.set_password(form.password1)
            return self.get(request)

class RoleView(LoginRequiredMixin, View):

    def get(self, request):
        roleID = request.GET.get('ID')

        try:
            role = models.Role.objects.get(id=roleID)
            dictionary = role.as_dict()
        except models.DoesNotExist:
            dictionary = None

        return render(request, 'audition_management/role.html', {
            "role": dictionary
        })

class RoleCreationView(LoginRequiredMixin, View):

    def get(self, request):
        form = RoleCreationForm()
        return render(request, 'audition_management/create.html', {'form': form})
    def post(self, request):
        form = RoleCreationForm(request.POST)
        if form.is_valid():
            role = models.Role(
                    name = form.name,
                    description = form.description,
                    domain = form.domain.current(),
                    studio_address = form.studio_address
            )
            role.save()
            return render(request, 'audition_management/role.html', {
                'role': role.as_dict()
            })
        else:
            return render(request, 'audition_management/create.html')
