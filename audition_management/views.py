from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib import messages
from audition_management import Role
from difflib import SequenceMatcher
from nltk.corpus import wordnet
# Create your views here.


class DashboardView(LoginRequiredMixin, View):

    def get(self, request):
        return render(request, 'audition_management/dashboard.html')


class RoleView(LoginRequiredMixin, View):

    def get(self, request, pk):
        role = Role.objects.get(pk=pk)
        dates = role.dates.all()
        return render(request, 'audition_management/role_view.html', {
            "role": role,
            "date": dates
        })


"""
    def similar(a, b):
        return SequenceMatcher(None, a, b).ratio()

    def get_word_synonyms_from_tags(role_tag, user_tags):
        role_tag_synonyms = []
        for synset in role_tagnet.synsets(role_tag.name):
            for lemma in synset.lemma_names():
                for tag in user_tags:
                    if tag.name == lemma:
                        role_tag_synonyms.append(lemma)
        return word_synonyms

    # fuzzy search algorithm
    roles = Role.objects.all()
    account = request.user.audition_account
    tags = account.tags.all()
    matching_roles = []
    for tag in tags:
        for role in roles:
            for role_tag in role.tags.all():
                similarity_index = similar(tag.name, role_tag.name)
                # confidence threshold of 80% chosen arbitrarily
                if similarity > .8:
                    matching_roles.append(role)
                    break
                else:
                    tag_synonyms = get_word_synonyms_from_tags(word, sent)
                    if len(tag_synonyms) > 0:
                        # synonym found.
                        matching_roles.append(role)
                        break
"""
