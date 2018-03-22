from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.views import View
from audition_management.models import (
    Role, AuditionAccount, CastingAccount, Tag, Application)
from audition_management.forms import SettingsForm
from difflib import SequenceMatcher
from nltk.corpus import wordnet
import json
# Create your views here.
from audition_management.forms import (
    RoleCreationForm, EventForm, EventFormSet, EditRoleForm,
    AuditionSettingsForm, TagFormSet, ProfileTagFormSet, PortfolioFormSet)


def is_casting_agent(current_user):
    """
    Returns true if the user has a casting agent account,
    Returns false otherwise.

    Errors if the user has no account.
    """
    user = None
    try:
        user = current_user.audition_account
        return False
    except AuditionAccount.DoesNotExist:
        try:
            user = current_user.casting_account
            return True
        except CastingAccount.DoesNotExist:
            pass
    return False


def is_audition_agent(current_user):
    """
    Returns true if the user has a audition_account account,
    Returns false otherwise.

    Errors if the user has no account.
    """
    user = None
    try:
        user = current_user.casting_account
        return False
    except CastingAccount.DoesNotExist:
        try:
            user = current_user.audition_account
            return True
        except AuditionAccount.DoesNotExist:
            pass
    return False


def get_user(current_user):
    user = None
    try:
        user = current_user.audition_account
    except AuditionAccount.DoesNotExist:
        try:
            user = current_user.casting_account
        except CastingAccount.DoesNotExist:
            pass
    return user


class DashboardView(LoginRequiredMixin, View):

    def similar(self, a, b):
        return SequenceMatcher(None, a, b).ratio()

    def get_word_synonyms_from_tags(self, role_tag, user_tags):
        role_tag_synonyms = []
        for synset in role_tag.net.synsets(role_tag.name):
            for lemma in synset.lemma_names():
                for tag in user_tags:
                    if tag.name == lemma:
                        role_tag_synonyms.append(lemma)
        return role_tag_synonyms

    def get_roles(self, request):
        roles = Role.objects.all()
        account = request.user.audition_account
        tags = account.tags.all()
        matching_roles = []
        for role in roles:
            role_score = 0
            for tag in tags:
                for role_tag in role.tags.all():
                    similarity_index = self.similar(tag.name, role_tag.name)
                    # confidence threshold of 80% chosen arbitrarily
                    if similarity_index > .8:
                        role_score += 1
                        break
                    else:
                        tag_synonyms = self.get_word_synonyms_from_tags(
                            tag.name, role_tag.name)
                        if len(tag_synonyms) > 0:
                            # synonym found.
                            role_score += 1
                            break
            if role_score > 0:
                matching_roles.append({'role': role, 'score': role_score})
        matching_roles_sorted = sorted(
            matching_roles, key=lambda k: k['score'], reverse=True)
        return [r['role'] for r in matching_roles_sorted]

    def get(self, request):
        # grabs all roles and returns them in JSON format for the SPA Framework
        # to use
        roles = self.get_roles(request)
        dictionaries = [obj.as_dict() for obj in roles]

        # Later, these roles will be filtered and ordered based on a number
        # of factors, the rough algorithm for which is found at the bottom of
        # the page.
        return render(request, 'audition_management/dashboard.html', {
            "roles": dictionaries,
            "is_casting": is_casting_agent(request.user),
            "is_audition": is_audition_agent(request.user),
        })


class AccountDelete(LoginRequiredMixin, View):
    def post(self, request, pk):
        user = User.objects.get(pk=pk)
        # only the user can delete his account. This is to protect from
        # malicious attacks
        if request.user != user:
            messages.error(request, "You cannot delete this account.")
            return HttpResponseRedirect(
                reverse("audition_management:settings"))
        else:
            user.delete()
            messages.success(request, "Account deleted.")
            return HttpResponseRedirect(reverse("session:login"))


class SettingsView(LoginRequiredMixin, View):

    def get_account_type(self, current_user):
        # this is for displaying to the user what account type they have
        try:
            current_user.audition_account
            return "Auditioner"
        except AuditionAccount.DoesNotExist:
            try:
                current_user.casting_account
                return "Casting Agent"
            except CastingAccount.DoesNotExist:
                pass
        return "None"

    def get(self, request):
        user = get_user(request.user)
        account_type = self.get_account_type(request.user)
        events = None
        if is_casting_agent(request.user):
            # grab all events made by the user
            events = user.roles.all()
            events = [obj.as_dict() for obj in events]
        else:
            # grab all applications made by this auditioner
            events = user.applications.all()
            events = [obj.as_dict() for obj in events]
            # this form is used to modify account non-password settings
            auditionform = AuditionSettingsForm(
                instance=request.user.audition_account)
            portfolioformset = PortfolioFormSet(prefix="form1")
            tagformset = ProfileTagFormSet(prefix="form1")
        form = SettingsForm(instance=request.user)
        # this is a Django Password Modification form
        change_password_form = PasswordChangeForm(request.user)
        if is_casting_agent(request.user):
            return render(request, 'session/settings.html', {
                'form': form,
                "change_password_form": change_password_form,
                "account_type": account_type,
                "is_casting": is_casting_agent(request.user),
                "roles": events
            })
        else:
            return render(request, 'session/settings.html', {
                'form': form,
                "change_password_form": change_password_form,
                "account_type": account_type,
                "is_casting": is_casting_agent(request.user),
                "audition_form": auditionform,
                "tag_form_set": tagformset,
                "portfolio_form_set": portfolioformset,
                "is_audition": is_audition_agent(request.user),
            })

    def post(self, request):
        # form_type is used to tell which form was submitted.
        if request.POST.get("form_type") == 'account_form':
            form = SettingsForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, "Account updated successfully.")
                return HttpResponseRedirect(
                    reverse("audition_management:settings"))
            else:
                # if the form isn't valid, we return the form with errors to
                # the user
                account_type = self.get_account_type(request.user)
                change_password_form = PasswordChangeForm(request.user)
                return render(request, 'session/settings.html', {
                    'form': form,
                    "change_password_form": change_password_form,
                    "account_type": account_type,
                    "is_casting": is_casting_agent(request.user)
                })
        elif request.POST.get("form_type") == 'audition_form':
            form = SettingsForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, "Account updated successfully.")
                return HttpResponseRedirect(
                    reverse("audition_management:settings"))
            else:
                account_type = self.get_account_type(request.user)
                account_form = SettingsForm(instance=request.user)
                change_password_form = PasswordChangeForm(request.user)
                tag_formset = ProfileTagFormSet(prefix="form1")
                portfolio_formset = PortfolioFormSet(prefix="form1")
                return render(request, 'session/settings.html', {
                    'form': account_form,
                    "change_password_form": change_password_form,
                    "account_type": account_type,
                    "is_casting": is_casting_agent(request.user),
                    "audition_form": form,
                    "tag_form_set": tag_formset,
                    "portfolio_form_set": portfolio_formset
                })
        elif request.POST.get("form_type") == 'tag_form_set':
            formset = ProfileTagFormSet(request.POST, prefix="form1")
            if formset.is_valid():
                for form in formset:
                    if form.is_valid():
                        tag = form.save(commit=False)
                        tag.account = request.account
                        tag.save()
                messages.success(
                    request, "Tags successfully added to posting.")
                return HttpResponseRedirect(
                    reverse("audition_management:settings"))
            else:
                account_type = self.get_account_type(request.user)
                account_form = SettingsForm(instance=request.user)
                change_password_form = PasswordChangeForm(request.user)
                audition_form = AuditionSettingsForm(instance=request.account)
                portfolio_formset = PortfolioFormSet(prefix="form1")
                return render(request, 'session/settings.html', {
                    'form': account_form,
                    "change_password_form": change_password_form,
                    "account_type": account_type,
                    "is_casting": is_casting_agent(request.user),
                    "audition_form": audition_form,
                    "tag_form_set": formset,
                    "portfolio_form_set": portfolio_formset
                })
        elif request.POST.get("form_type") == 'portfolio_form_set':
            formset = PortfolioFormSet(request.POST, prefix="form1")
            if formset.is_valid():
                for form in formset:
                    if form.is_valid():
                        pastwork = form.save(commit=False)
                        pastwork.account = request.account
                        pastwork.save()
                messages.success(
                    request, "Tags successfully added to posting.")
                return HttpResponseRedirect(
                    reverse("audition_management:settings"))
            else:
                account_type = self.get_account_type(request.user)
                account_form = SettingsForm(instance=request.user)
                audition_form = AuditionSettingsForm(instance=request.account)
                change_password_form = PasswordChangeForm(request.user)
                tag_formset = ProfileTagFormSet(prefix="form1")
                return render(request, 'session/settings.html', {
                    'form': account_form,
                    "change_password_form": change_password_form,
                    "account_type": account_type,
                    "is_casting": is_casting_agent(request.user),
                    "audition_form": audition_form,
                    "tag_form_set": tag_formset,
                    "portfolio_form_set": formset
                })
        else:
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password changed successfully.")
                return HttpResponseRedirect(
                    reverse("audition_management:settings"))
            else:
                account_type = self.get_account_type(request.user)
                account_form = SettingsForm(instance=request.user)
                return render(request, 'session/settings.html', {
                    'form': account_form,
                    "change_password_form": form,
                    "account_type": account_type,
                    "is_casting": is_casting_agent(request.user)
                })


class RoleView(LoginRequiredMixin, View):

    def get(self, request, pk):
        role = Role.objects.get(id=pk)
        auditions = role.applications.all()
        auditions = [obj.as_dict() for obj in auditions]
        return render(request, 'audition_management/role.html', {
            "role": role,
            "is_casting": is_casting_agent(request.user),
            "auditions": auditions
        })

    def post(self, request, pk):
        role = Role.objects.get(id=pk)
        if not is_casting_agent(request.user):
            audition_account = request.user.audition_account
            Application.objects.create(
                user=audition_account, posting=role)
            messages.success(
                request, "Audition request has been sent. The casting agent will be in touch with you.")
            return HttpResponseRedirect(
                reverse("audition_management:role", args=[role.id]))
        else:
            application_pk = request.POST.get("pk")
            Application.objects.get(pk=application_pk).delete()
            messages.success(request, "Application deleted")
            return HttpResponseRedirect(
                reverse("audition_management:role", args=[role.id]))


class UserView(LoginRequiredMixin, View):
    def get(self, request, pk):

        user = User.objects.get(pk=pk)
        events = None
        is_casting = is_casting_agent(user)
        if is_casting:
            user = user.casting_account
            # grab all events made by the user
            events = user.roles.all()
            events = [obj.as_dict() for obj in events]
        else:
            user = user.audition_account
            # grab all applications made by this auditioner
            events = user.applications.all()
            events = [obj.posting.as_dict() for obj in events]
        return render(request, 'session/external_profile.html', {
            "external_user": user,
            "is_casting": is_casting_agent(request.user),
            "user_is_casting": is_casting,
            "roles": events
        })


class RoleCreationView(LoginRequiredMixin, View):

    def get(self, request):
        # prefixs are used to differentiate which forms are which on submit
        form = RoleCreationForm(prefix="form1")
        formset = EventFormSet(prefix="form2")
        return render(request, 'audition_management/create.html', {
            'form': form,
            "formset": formset
        })

    def post(self, request):
        form = RoleCreationForm(request.POST, prefix="form1")
        formset = EventFormSet(request.POST, prefix="form2")
        role = None
        if form.is_valid():
            role = form.save(commit=False)
            role.agent = request.user.casting_account
            role.save()
        else:
            return render(request, 'audition_management/create.html', {
                'form': form,
                "formset": formset
            })
        if formset.is_valid() is False:
            messages.error(
                request, "Please review the forms and try again.")
            return render(request, 'audition_management/create.html', {
                'form': form,
                "formset": formset
            })
        else:
            for form in formset:
                if form.is_valid():
                    event = form.save(commit=False)
                    event.role = role
                    event.save()
            messages.success(
                request, "Role successfully created.")
            return HttpResponseRedirect(
                reverse("audition_management:tags", args=[role.id]))


class TagCreationView(LoginRequiredMixin, View):
    def get(self, request, pk):
        # after role creation, tags must be added.
        role = Role.objects.get(pk=pk)
        formset = TagFormSet(prefix="form1")
        return render(request, "audition_management/addTags.html", {
            "role": role,
            "formset": formset,
        })

    def post(self, request, pk):
        role = Role.objects.get(pk=pk)
        formset = TagFormSet(request.POST, prefix="form1")
        if formset.is_valid() is False:
            messages.error(
                request, "Please review the forms and try again.")
            return render(request, 'audition_management/addTags.html', {
                'role': role,
                "formset": formset
            })
        else:
            for form in formset:
                if form.is_valid():
                    tag = form.save(commit=False)
                    tag.role = role
                    tag.save()
            messages.success(
                request, "Tags successfully added to posting.")
            return HttpResponseRedirect(
                reverse("audition_management:settings"))


class EditRoleView(LoginRequiredMixin, View):

    def get(self, request, pk):
        role = Role.objects.get(pk=pk)
        form = EditRoleForm(instance=role, prefix="form1")
        formset = EventFormSet(instance=role, prefix="form2")
        return render(request, 'audition_management/editRole.html', {
            'role': role,
            'form': form,
            'formset': formset,
            "is_casting": is_casting_agent(request.user)
        })

    def post(self, request, pk):
        role = Role.objects.get(pk=pk)
        update_tags = json.loads(request.POST.get("update_tags"))
        form = EditRoleForm(request.POST, instance=role, prefix="form1")
        if form.is_valid():
            role = form.save()
            formset = EventFormSet(request.POST, instance=role, prefix="form2")
            for form in formset:
                # if the form is valid and hasn't been marked to be deleted, we
                # create the event.
                if (form.is_valid() and
                        form.cleaned_data.get('DELETE') is False):
                    event = form.save(commit=False)
                    event.role = role
                    event.save()
                # if the form is valid and has been marked for deletion, we
                # delete the form without creating the event.
                elif (form.cleaned_data.get('DELETE') is True):
                    form.cleaned_data.get('id').delete()
                elif form.is_valid() is False:
                    role = Role.objects.get(pk=pk)
                    form = EditRoleForm(instance=role, prefix="form1")
                    return render(
                        request,
                        'audition_management/editRole.html',
                        {
                            'role': role,
                            'form': form,
                            'formset': formset,
                            "is_casting": is_casting_agent(request.user)
                        }
                    )
            # tags do not need to be preserved, so we nuke and readd
            role.tags.all().delete()
            for tag in update_tags:
                Tag.objects.create(name=tag["tag"], role=role)
            messages.success(request, "Role successfully updated.")
            return HttpResponseRedirect(
                reverse("audition_management:edit-role", args=[pk]))
        else:
            role = Role.objects.get(pk=pk)
            formset = EventFormSet(instance=role, prefix="form2")
            return render(request, 'audition_management/editRole.html', {
                'role': role,
                'form': form,
                'formset': formset,
                "is_casting": is_casting_agent(request.user)
            })


"""
    This will be used in sprint 2
    def similar(a, b):
        return SequenceMatcher(None, a, b).ratio()
    def get(self, request, pk):
        user = User.objects.get(pk=pk)
        audition_account = user.audition_account
        tags = audition_account.tags.all()
        applied_events = Role.objects.filter()
        is_own_profile = False

        #if the current user is visiting their own profile
        if (str(request.user.id) == pk):
            is_own_profile = True

        return render(request, 'audition_management/auditionProfile.html', {
            "is_audition": is_audition_agent(request.user),
            "is_own_profile": is_own_profile,
            'user': audition_account
        })

class CastingProfileView(LoginRequiredMixin, View):

    def get(self, request, pk):
        user = User.objects.get(pk=pk)
        print(user)
        return render(request, 'audition_management/castingProfile.html', {
            "user": user
        })
"""
