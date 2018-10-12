from django.contrib.auth.views import LogoutView, LoginView
from django.urls import reverse_lazy, path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('challenges/', views.ChallengesView.as_view(), name='challenges'),
    path('challenges/<int:id>/', views.ChallengeDetailsView.as_view(), name='challenge-details'),
    path('challenges/<int:challenge_id>/hint', views.reveal_hint, name='challenge-hint'),
    path('scoreboard/', views.ScoreboardView.as_view(), name='scoreboard'),
    path('rules/', views.RulesView.as_view(), name='rules'),
    path('about_us/', views.AboutUsView.as_view(), name='about-us'),
    path('links/', views.LinksView.as_view(), name='links'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('index')), name='logout'),
    path('login/', LoginView.as_view(template_name='wargame/login_form.html'), name='login'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('registration-disallowed/', TemplateView.as_view(template_name='wargame/registration_disallowed.html'), name='django_registration_disallowed'),
    path('vpn/', views.VPNView.as_view(), name='vpn-info'),
    path('vpn/key', views.download_vpn_key, name='vpn-key'),
    path('challenge-files/<int:file_id>', views.download_challenge_file, name='challenge-file'),
    path('user/set-email', views.UserEmailView.as_view(), name="user-set-email"),
]

