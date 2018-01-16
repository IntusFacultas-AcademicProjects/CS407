from django.core.urlresolvers import reverse
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from session.forms import SignUpForm


def signup(request):
    print("test")
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.save()
            messages.success(request, "Account created. Please log in.")
            return HttpResponseRedirect(reverse('session:login'))
    else:
        print("test")
        form = SignUpForm()
        return render(request, 'session/signup.html', {'form': form})
