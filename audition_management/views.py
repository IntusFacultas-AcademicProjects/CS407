import requests
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.views import View
from audition_management.models import (
    Role, AuditionAccount, CastingAccount, Tag, Application, Alert, Message,
    RoleViewModel, DeletedApplication)
from audition_management.forms import SettingsForm
from difflib import SequenceMatcher
from nltk.corpus import wordnet
import json
# Create your views here.
from audition_management.forms import (
    RoleCreationForm, EventFormSet, EditRoleForm,
    AuditionSettingsForm, CastingSettingsForm, TagFormSet, ProfileTagFormSet,
    PortfolioFormSet)
from pygeocoder import Geocoder
import geopy.distance
from pygeolib import GeocoderError


def email_user(context, contact_email):
    """
    context is a JSON object in the format of:

    {
        'user': Django user object,
        "message": String,
    }
    contact_email is the email to be sent to
    """
    message = render_to_string(
        'audition_management/email.html',
        context)
    send_mail(
        'AuditionMe Alert',
        message,
        "postmaster@sandbox5a43426cc809431499f0413215c63ae3.mailgun.org",
        [contact_email],
        fail_silently=False,
    )


def is_casting_agent(current_user):
    """
    Returns true if the user has a casting agent account,
    Returns false otherwise.

    Errors if the user has no account.
    """
    try:
        current_user.audition_account
        return False
    except AuditionAccount.DoesNotExist:
        try:
            current_user.casting_account
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
    try:
        current_user.casting_account
        return False
    except CastingAccount.DoesNotExist:
        try:
            current_user.audition_account
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
        for synset in wordnet.synsets(role_tag):
            for lemma in synset.lemma_names():
                if user_tags == lemma:
                    role_tag_synonyms.append(lemma)
        return role_tag_synonyms

    def get_roles(self, request):
        def compare_roles(a, b):
            print(a["score"])
            print(b["score"])
            if (a["score"] > b["score"]):
                return 1
            elif (b["score"] > a["score"]):
                return -1
            else:
                if a["distance"] > b["distance"]:
                    return 1
                elif b["distance"] > a["distance"]:
                    return -1
                else:
                    return 0

        def cmp_to_key(mycmp):
            class K:
                def __init__(self, obj, *args):
                    self.obj = obj

                def __lt__(self, other):
                    return mycmp(self.obj, other.obj) < 0

                def __gt__(self, other):
                    return mycmp(self.obj, other.obj) > 0

                def __eq__(self, other):
                    return mycmp(self.obj, other.obj) == 0

                def __le__(self, other):
                    return mycmp(self.obj, other.obj) <= 0

                def __ge__(self, other):
                    return mycmp(self.obj, other.obj) >= 0

                def __ne__(self, other):
                    return mycmp(self.obj, other.obj) != 0
            return K
        roles = Role.objects.filter(status=1)
        account = request.user.audition_account
        tags = account.tags.all()
        matching_roles = []
        for role in roles:
            if account.denied_applications.filter(posting__pk=role.id).count() > 0:
                continue
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
                            role_tag.name, tag.name)
                        if len(tag_synonyms) > 0:
                            # synonym found.
                            role_score += 1
                            break
            if role_score > 0:
                # distance is a big number at first so low priority until changed
                distance = 1000000000
                try:
                    role_location = Geocoder.geocode(role.studio_address)
                    user_location = Geocoder.geocode(account.location)
                    distance = geopy.distance.vincenty(
                        role_location.coordinates,
                        user_location.coordinates
                    ).km
                except GeocoderError as e:
                    if e.status == "ZERO_RESULTS":
                        print("location doesn't exist")
                    else:
                        print("API Failure")
                matching_roles.append(
                    {
                        'role': role,
                        'score': role_score,
                        'distance': distance
                    }
                )

        matching_roles_sorted = sorted(
            matching_roles, key=cmp_to_key(compare_roles), reverse=True)
        print(matching_roles_sorted)
        return [r['role'] for r in matching_roles_sorted]

    def get(self, request):
        # grabs all roles and returns them in JSON format for the SPA Framework
        # to use
        # email_user({
        #     "user": request.user,
        #     "message": "Fuck you pal"
        # }, request.user.email)
        if not is_casting_agent(request.user):
            roles = self.get_roles(request)
        else:
            roles = Role.objects.filter(status=1)
        dictionaries = [obj.as_dict() for obj in roles]
        print(dictionaries)
        all_roles_dictionaries = [obj.as_dict()
                                  for obj in Role.objects.filter(status=1)]
        print(all_roles_dictionaries)

        # Later, these roles will be filtered and ordered based on a number
        # of factors, the rough algorithm for which is found at the bottom of
        # the page.
        return render(request, 'audition_management/dashboard.html', {
            "roles": dictionaries,
            "all_roles": all_roles_dictionaries,
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
        portfolioformset = None
        if is_casting_agent(request.user):
            # grab all events made by the user
            events = user.roles.all()
            events = [obj.as_dict() for obj in events]
            # this form is used to modify account non-password settings
            castingform = CastingSettingsForm(
                instance=request.user.casting_account)
        else:
            # grab all applications made by this auditioner
            try:
                events = user.applications.all()
            except AttributeError:
                events = []
            events = [obj.as_dict() for obj in events]
            # this form is used to modify account non-password settings
            auditionform = AuditionSettingsForm(
                instance=request.user.audition_account)
            portfolioformset = PortfolioFormSet(
                instance=request.user.audition_account,
                prefix="form1")
            tagformset = ProfileTagFormSet(prefix="form2")

        form = SettingsForm(instance=request.user)
        # this is a Django Password Modification form
        change_password_form = PasswordChangeForm(request.user)
        if is_casting_agent(request.user):
            return render(request, 'session/settings.html', {
                'form': form,
                "change_password_form": change_password_form,
                "account_type": account_type,
                "is_casting": is_casting_agent(request.user),
                "roles": events,
                "casting_form": castingform
            })
        else:
            return render(request, 'session/settings.html', {
                'form': form,
                "change_password_form": change_password_form,
                "account_type": account_type,
                "is_casting": is_casting_agent(request.user),
                "audition_form": auditionform,
                "portfolio_formset": portfolioformset,
            })

    def post(self, request):
        print("posted")
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
                if is_casting_agent(request.user):
                    # grab all events made by the user
                    events = request.user.roles.all()
                    events = [obj.as_dict() for obj in events]
                    castingform = CastingSettingsForm(
                        instance=request.user.casting_account)
                    return render(request, 'session/settings.html', {
                        'form': form,
                        "change_password_form": change_password_form,
                        "account_type": account_type,
                        "is_casting": is_casting_agent(request.user),
                        "roles": events,
                        "casting_form": castingform
                    })
                else:
                    # grab all applications made by this auditioner
                    events = request.user.applications.all()
                    events = [obj.as_dict() for obj in events]
                    # this form is used to modify account non-password settings
                    auditionform = AuditionSettingsForm(
                        instance=request.user.audition_account)
                    portfolioformset = PortfolioFormSet(
                        instance=request.user.audition_account,
                        prefix="form1")
                    return render(request, 'session/settings.html', {
                        'form': form,
                        "change_password_form": change_password_form,
                        "account_type": account_type,
                        "is_casting": is_casting_agent(request.user),
                        "audition_form": auditionform,
                        "portfolio_formset": portfolioformset,
                    })
        elif request.POST.get("form_type") == 'audition_form':
            form = AuditionSettingsForm(
                request.POST, instance=request.user.audition_account)
            if form.is_valid():
                ethnic_choices = []
                gender_choices = []
                for tup in AuditionAccount.ETHNICITY_CHOICES:
                    ethnic_choices.append(tup[1])
                for tup in AuditionAccount.GENDER_CHOICES:
                    gender_choices.append(tup[1])
                for tag in request.user.audition_account.tags.all():
                    if (tag.name in ethnic_choices or
                            tag.name in gender_choices):
                        tag.delete()
                if form.cleaned_data['ethnicity'] is not None:
                    Tag.objects.create(
                        name=AuditionAccount.ETHNICITY_CHOICES[
                            form.cleaned_data['ethnicity']][1],
                        account=request.user.audition_account)
                if form.cleaned_data['gender'] is not None:
                    Tag.objects.create(
                        name=AuditionAccount.GENDER_CHOICES[
                            form.cleaned_data['gender']][1],
                        account=request.user.audition_account)
                form.save()
                messages.success(request, "Account updated successfully.")
                return HttpResponseRedirect(
                    reverse("audition_management:settings"))
            else:
                account_type = self.get_account_type(request.user)
                account_form = SettingsForm(instance=request.user)
                change_password_form = PasswordChangeForm(request.user)
                portfolio_formset = PortfolioFormSet(prefix="form1")
                return render(request, 'session/settings.html', {
                    'form': account_form,
                    "change_password_form": change_password_form,
                    "account_type": account_type,
                    "is_casting": is_casting_agent(request.user),
                    "audition_form": form,
                    "portfolio_formset": portfolio_formset
                })
        elif request.POST.get("form_type") == 'casting_form':
            form = CastingSettingsForm(
                request.POST, instance=request.user.casting_account)
            if form.is_valid():
                form.save()
                messages.success(request, "Account updated successfully.")
                return HttpResponseRedirect(
                    reverse("audition_management:settings"))
            else:
                account_type = self.get_account_type(request.user)
                account_form = SettingsForm(instance=request.user)
                change_password_form = PasswordChangeForm(request.user)
                # grab all events made by the user
                events = request.user.roles.all()
                events = [obj.as_dict() for obj in events]
                return render(request, 'session/settings.html', {
                    'form': account_form,
                    "change_password_form": change_password_form,
                    "account_type": account_type,
                    "is_casting": is_casting_agent(request.user),
                    "roles": events,
                    "casting_form": form
                })
        elif request.POST.get("form_type") == 'tag_formset':
            update_tags = json.loads(request.POST.get("update_tags"))
            request.user.audition_account.tags.all().delete()
            for tag in update_tags:
                Tag.objects.create(
                    name=tag["tag"], account=request.user.audition_account)
            messages.success(
                request, "Tags successfully updated.")
            return HttpResponseRedirect(
                reverse("audition_management:settings"))
        elif request.POST.get("form_type") == 'portfolio_formset':
            formset = PortfolioFormSet(
                request.POST,
                prefix="form1",
                instance=request.user.audition_account)
            if formset.is_valid():
                for form in formset:
                    if (form.is_valid() and
                            form.cleaned_data.get('DELETE') is False):
                        pastwork = form.save(commit=False)
                        pastwork.account = request.user.audition_account
                        pastwork.save()
                    elif (form.cleaned_data.get('DELETE') is True):
                        form.cleaned_data.get('id').delete()
                messages.success(
                    request, "Portfolio successfully updated.")
                return HttpResponseRedirect(
                    reverse("audition_management:settings"))
            else:
                account_type = self.get_account_type(request.user)
                account_form = SettingsForm(instance=request.user)
                audition_form = AuditionSettingsForm(
                    instance=request.user.audition_account)
                change_password_form = PasswordChangeForm(request.user)
                print(formset.errors)
                messages.error(
                    request, "Please review your input and try again.")
                return render(request, 'session/settings.html', {
                    'form': account_form,
                    "change_password_form": change_password_form,
                    "account_type": account_type,
                    "is_casting": is_casting_agent(request.user),
                    "audition_form": audition_form,
                    "portfolio_formset": formset
                })
        elif request.POST.get("form_type") == 'delete':
            Role.objects.get(pk=request.POST.get("pk")).delete()
            messages.success(
                request, "Role Successfully Deleted")
            return HttpResponseRedirect(
                reverse("audition_management:settings"))
        else:
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password changed successfully.")
                return HttpResponseRedirect(
                    reverse("audition_management:settings"))
            else:
                account_form = SettingsForm(instance=request.user)
                account_type = self.get_account_type(request.user)
                if is_casting_agent(request.user):
                    return render(request, 'session/settings.html', {
                        'form': account_form,
                        "change_password_form": form,
                        "account_type": account_type,
                        "is_casting": is_casting_agent(request.user),
                        "roles": events
                    })
                else:
                    auditionform = AuditionSettingsForm(
                        instance=request.user.audition_account)
                    portfolioformset = PortfolioFormSet(
                        instance=request.user.audition_account,
                        prefix="form1")
                    return render(request, 'session/settings.html', {
                        'form': account_form,
                        "change_password_form": form,
                        "account_type": account_type,
                        "is_casting": is_casting_agent(request.user),
                        "audition_form": auditionform,
                        "portfolio_formset": portfolioformset,
                    })


class RoleView(LoginRequiredMixin, View):

    def get(self, request, pk):
        role = Role.objects.get(id=pk)
        auditions = role.applications.all()
        auditions = [obj.as_dict() for obj in auditions]
        if (not is_casting_agent(request.user) and
                request.user.audition_account.roleview is None):
            newview = RoleViewModel(role=role, account=request.user)
            newview.save()
        views = RoleViewModel.objects.filter(role=role).count()
        return render(request, 'audition_management/role.html', {
            "role": role,
            "is_casting": is_casting_agent(request.user),
            "auditions": auditions,
            "views": views
        })

    def post(self, request, pk):
        role = Role.objects.get(id=pk)
        if not is_casting_agent(request.user):
            audition_account = request.user.audition_account
            Application.objects.create(
                user=audition_account, posting=role)
            text = "{} has applied for the role {}.".format(
                request.user.audition_account, role)
            Alert.objects.create(
                text=text,
                account=role.agent.profile)
            email_user({
                "user": role.agent.profile,
                "message": "{} {} has applied for your role: {}".format(
                    request.user.first_name,
                    request.user.last_name,
                    role.name
                )
            }, role.agent.profile.email)
            messages.success(
                request,
                "Audition request has been sent. The casting \
                     agent will be in touch with you.")
            return HttpResponseRedirect(
                reverse("audition_management:role", args=[role.id]))
        else:
            application_pk = request.POST.get("pk")
            application = Application.objects.get(pk=application_pk)
            role = application.posting
            Alert.objects.create(
                text="Your application for role # {} has been deleted.".format(
                    role.id),
                account=application.user.profile)
            DeletedApplication.objects.create(
                user=application.user,
                posting=application.posting
            )
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
            events = user.roles.filter(status=1)
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
                print(form.empty_permitted)
                print(form.has_changed())
                if form.is_valid() and form.has_changed():
                    event = form.save(commit=False)
                    event.role = role
                    role.views = 0
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
                if form.is_valid() and form.has_changed():
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
                    print(form.data)
                    print(form.cleaned_data)
                    role = Role.objects.get(pk=pk)
                    form = EditRoleForm(instance=role, prefix="form1")
                    messages.error(
                        request, "Please review your data and try again.")
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
            messages.error(request, "Please review your data and try again.")
            return render(request, 'audition_management/editRole.html', {
                'role': role,
                'form': form,
                'formset': formset,
                "is_casting": is_casting_agent(request.user)
            })


class InvitationView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if not is_casting_agent(request.user):
            messages.error(
                request,
                "You cannot invite someone to a role if you are \
                not the owner of that role"
            )
            return HttpResponseRedirect(request.POST.get("url_of_request"))
        user = User.objects.get(pk=pk)
        role = Role.objects.get(pk=request.POST.get("role_pk"))
        text = "{} has invited you to another round of auditions for {}. Arrange \
             a time with them over email.".format(
            request.user.casting_account,
            role
        )
        email_user({
            "user": user,
            "message": text
        }, user.email)
        Alert.objects.create(
            text=text,
            account=user
        )
        messages.success(request,
                         "User has been invited to another round of auditions.")
        return HttpResponseRedirect(request.POST.get("url_of_request"))


class MessageView(LoginRequiredMixin, View):

    def get(self, request, pk):
        return render(request, 'audition_management/chats.html', {

        })

    def post(self, request, pk):
        alert = Alert.objects.get(pk=pk)
        if request.user != alert.account:
            messages.error(request, "Alert does not exist.")
            return HttpResponseRedirect(request.POST.get("url_of_request"))
        else:
            alert.delete()
            return HttpResponseRedirect(request.POST.get("url_of_request"))


class ChatView(LoginRequiredMixin, View):
    """
    This does not return a HTML document. This is an AJAX only view
    specifically for use with a Vue document.
    """

    def get(self, request):
        user = request.user
        messaged_users = user.sent_messages.all().values('receiver').distinct()
        message_chats = []
        for receiver in messaged_users:
            messages_sent = user.sent_messages.filter(
                receiver=receiver["receiver"])
            messages_received = user.received_messages.filter(
                sender=receiver["receiver"])
            messages = messages_sent | messages_received
            messages = messages.order_by("timestamp")
            message_logs = [obj.as_dict() for obj in messages]
            receiver_django = User.objects.get(pk=receiver["receiver"])
            message_chats.append({
                "participant": {
                    "pk": receiver["receiver"],
                    "name": receiver_django.first_name + " " +
                    receiver_django.last_name
                },
                "messages": json.dumps(message_logs)
            })
        for messenger in user.received_messages.all().values('sender').distinct():
            count = user.sent_messages.filter(receiver=messenger['sender']).count()
            print("{}".format(count))
            if user.sent_messages.filter(receiver=messenger['sender']).count() > 0:
                continue
            messages_received = user.received_messages.filter(sender=messenger['sender'])
            messages_received = messages_received.order_by("timestamp")
            message_logs = [obj.as_dict() for obj in messages_received]
            messenger_django = User.objects.get(pk=messenger["sender"])
            message_chats.append({
                "participant": {
                    "pk": messenger['sender'].id,
                    "name": messenger_django.first_name + " " +
                    messenger_django.last_name
                },
                "messages": json.dumps(message_logs)
            })
        return JsonResponse({
            "data": message_chats,
        })

    def post(self, request):
        # in all fairness, this is pretty unsafe. No checks made.
        receiver_pk = request.POST.get("receiver")
        text = request.POST.get("text")
        sender = request.user
        receiver = User.objects.get(pk=receiver_pk)
        Message.objects.create(
            receiver=receiver,
            sender=sender,
            text=text
        )
        Alert.objects.create(
            text="New message from {}".format(sender.first_name),
            account=receiver)

        return HttpResponse("Ok", status=200)


class ConversationView(LoginRequiredMixin, View):

    def get(self, request):

        user = request.user
        messaged_users = user.sent_messages.all().values('receiver').distinct()
        message_chats = []
        for receiver in messaged_users:
            messages_sent = user.sent_messages.filter(
                receiver=receiver["receiver"])
            messages_received = user.received_messages.filter(
                sender=receiver["receiver"])
            messages = messages_sent | messages_received
            messages = messages.order_by("timestamp")
            message_logs = [obj.as_dict() for obj in messages]
            receiver_django = User.objects.get(pk=receiver["receiver"])
            message_chats.append({
                "participant": {
                    "pk": receiver["receiver"],
                    "name": receiver_django.first_name + " " +
                    receiver_django.last_name
                },
                "messages": message_logs
            })
        print(message_chats)
        return render(request, 'audition_management/messages.html', {
            'user': user,
            'data': message_chats

        })


class SendView(LoginRequiredMixin, View):

    def get(self, request, pk):
        receiver = User.objects.get(pk=pk)
        is_casting = is_casting_agent(receiver)
        if is_casting:
            receiver = receiver.casting_account
        else:
            receiver = receiver.audition_account
        print(receiver)
        return render(request, 'audition_management/send.html', {
            'receiver': receiver,
            'pk': pk
        })
