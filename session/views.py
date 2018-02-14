from django.core.urlresolvers import reverse
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from session.forms import SignUpForm
from audition_management.models import CastingAccount, AuditionAccount


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.save()
            if request.POST.get("account_type") == "0":
                CastingAccount.objects.create(profile=user)
            elif request.POST.get("account_type") == "1":
                AuditionAccount.objects.create(profile=user)
            else:
                print(request.POST.get("account_type"))
            messages.success(request, "Account created. Please log in.")
            return HttpResponseRedirect(reverse('session:login'))
    else:
        form = SignUpForm()
        return render(request, 'session/signup.html', {'form': form})
