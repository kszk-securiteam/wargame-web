from django.contrib.auth.views import LogoutView, LoginView
from django.urls import reverse_lazy, path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('challenges', views.ChallengesView.as_view(), name='challenges'),
    path('scoreboard', views.ScoreboardView.as_view(), name='scoreboard'),
    path('rules', views.RulesView.as_view(), name='rules'),
    path('about_us', views.AboutUsView.as_view(), name='about-us'),
    path('links', views.LinksView.as_view(), name='links'),
    path('logout', LogoutView.as_view(next_page=reverse_lazy('index')), name='logout'),
    path('login', LoginView.as_view(template_name='login_form.html'), name='login'),
]

