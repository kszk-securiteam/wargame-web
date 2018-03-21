from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = 'index.html'


class ChallengesView(TemplateView):
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
