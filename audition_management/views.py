from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib import messages
# Create your views here.


class DashboardView(LoginRequiredMixin, View):

    def get(self, request):
        return render(request, 'audition_management/dashboard.html')
