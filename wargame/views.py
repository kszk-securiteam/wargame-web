from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from registration.backends.simple.views import RegistrationView

from forms import UserRegistrationForm


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
