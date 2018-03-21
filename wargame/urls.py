from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('challenges', views.ChallengesView.as_view(), name='challenges'),
    path('scoreboard', views.ScoreboardView.as_view(), name='scoreboard'),
    path('rules', views.RulesView.as_view(), name='rules'),
    path('about_us', views.AboutUsView.as_view(), name='about-us'),
    path('links', views.LinksView.as_view(), name='links'),
]

