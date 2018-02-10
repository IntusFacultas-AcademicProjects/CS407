from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib import messages
# Create your views here.
from audition_management import models
from audition_management.forms import RoleCreationForm


class DashboardView(LoginRequiredMixin, View):

    def get(self, request):
        return render(request, 'audition_management/dashboard.html')

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
