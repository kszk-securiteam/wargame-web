from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path, reverse_lazy
from django.views.generic import RedirectView

from wargame_admin.views import ChallengeListView, ChallengeDetailsView, ChallengeEditView, UserAdminView, \
    SubmissionAdminView, ConfigEditorView, ChallengeCreateView, ChallengeDeleteView, ChallengeFilesView, \
    ChallengeFileDeleteView

app_name = 'wargame-admin'
urlpatterns = [
    path('', RedirectView.as_view(url=reverse_lazy('wargame-admin:challenges')), name='index'),
    path('challenges/', staff_member_required(ChallengeListView.as_view()), name='challenges'),
    path('challenges/<int:pk>/', staff_member_required(ChallengeDetailsView.as_view()), name='challenge-details'),
    path('challenges/<int:pk>/edit', staff_member_required(ChallengeEditView.as_view()), name='challenge-edit'),
    path('challenges/<int:pk>/delete', staff_member_required(ChallengeDeleteView.as_view()), name='challenge-delete'),
    path('challenges/<int:pk>/files', staff_member_required(ChallengeFilesView.as_view()), name='challenge-files'),
    path('files/<int:pk>/delete', staff_member_required(ChallengeFileDeleteView.as_view()), name='challenge-file-delete'),
    path('challenges/new', staff_member_required(ChallengeCreateView.as_view()), name='challenge-create'),
    path('users/', staff_member_required(UserAdminView.as_view()), name='users'),
    path('submissions/', staff_member_required(SubmissionAdminView.as_view()), name='submissions'),
    path('config/', staff_member_required(ConfigEditorView.as_view()), name='config')
]
