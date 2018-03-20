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


class LinksView(TemplateView):
    template_name = 'links.html'
