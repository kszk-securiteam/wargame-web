from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic import TemplateView
from registration.backends.simple.views import RegistrationView
from wargame import models

from wargame.forms import UserRegistrationForm
from wargame.models import Challenge, Tag, UserChallenge, Submission


class IndexView(TemplateView):
    template_name = 'index.html'


class ChallengesView(LoginRequiredMixin, TemplateView):
    template_name = 'challenges.html'


class ScoreboardView(TemplateView):
    template_name = 'scoreboard.html'


class RulesView(TemplateView):
    template_name = 'rules.html'


class AboutUsView(TemplateView):
    template_name = 'about_us.html'

    def get_people(self):
        names = ['Szász Márton', 'Márki-Zay Ferenc', 'Schulcz Ferenc',
                 'Madarász Bence', 'Hegyi Zsolt', 'Kovács Bence',
                 'Barkaszi Richárd', 'Bakos Ádám']
        names.sort()
        return names


class LinksView(TemplateView):
    template_name = 'links.html'


class UserRegistrationView(RegistrationView):
    form_class = UserRegistrationForm
    template_name = 'registration.html'


class ChallengeDetailsView(TemplateView):
    template_name = 'challenge_details.html'

    def challenge(self):
        return Challenge.objects.get(pk=self.kwargs['id'])

    def userchallenge(self):
        return UserChallenge.get_or_create(self.request.user, self.challenge())

    def post(self, *args, **kwargs):
        userchallenge = self.userchallenge()
        if userchallenge.solved():
            return HttpResponseRedirect(self.request.path)

        submission = Submission()
        submission.user_challenge = userchallenge
        submission.value = self.request.POST.get('flag')

        if submission.value is None:
            return HttpResponseRedirect(self.request.path)

        submission.save()

        if userchallenge.solved():
            messages.success(self.request, 'Congratulations! You have successfully solved this challenge!')
        else:
            messages.error(self.request, 'Your answer was incorrect. Try again!')

        return HttpResponseRedirect(self.request.path)
