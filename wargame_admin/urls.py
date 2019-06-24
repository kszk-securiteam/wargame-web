from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path, reverse_lazy
from django.views.generic import RedirectView

from wargame_admin.views import ChallengeListView, ChallengeDetailsView, ChallengeEditView, UserAdminView, \
    ConfigEditorView, ChallengeCreateView, ChallengeDeleteView, ChallengeFilesView, \
    ChallengeFileDeleteView, ChallengeSubmissions, UserSubmissions, UserEdit, ResetHintsView, ClearSubmissionsView, \
    StaffMemberAdmin, StaffEditView, StaffCreateView, StaffDeleteView, \
    challenge_export_view, ChallengeFileChunkedUploadView, ChallengeFileChunkedUploadCompleteView, StaticEditorList, \
    StaticEditor, ImportExportView, log_view, export_download, ExportDeleteView, RebalanceView

app_name = 'wargame-admin'
urlpatterns = [
    path('', RedirectView.as_view(url=reverse_lazy('wargame-admin:challenges')), name='index'),
    path('challenges/', staff_member_required(ChallengeListView.as_view()), name='challenges'),
    path('challenges/<int:pk>/', staff_member_required(ChallengeDetailsView.as_view()), name='challenge-details'),
    path('challenges/<int:pk>/edit', staff_member_required(ChallengeEditView.as_view()), name='challenge-edit'),
    path('challenges/<int:pk>/delete', staff_member_required(ChallengeDeleteView.as_view()), name='challenge-delete'),
    path('challenges/<int:pk>/files', staff_member_required(ChallengeFilesView.as_view()), name='challenge-files'),
    path('challenge-submissions/', staff_member_required(ChallengeSubmissions.as_view()), name='challenge-submissions'),
    path('user-submissions/', staff_member_required(UserSubmissions.as_view()), name='user-submissions'),
    path('submissions/reset-hint', staff_member_required(ResetHintsView.as_view()), name='submission-reset-hint'),
    path('submissions/clear', staff_member_required(ClearSubmissionsView.as_view()), name='submission-clear'),
    path('files/<int:pk>/delete', staff_member_required(ChallengeFileDeleteView.as_view()), name='challenge-file-delete'),
    path('challenges/new', staff_member_required(ChallengeCreateView.as_view()), name='challenge-create'),
    path('users/', staff_member_required(UserAdminView.as_view()), name='users'),
    path('users/<int:pk>/', staff_member_required(UserEdit.as_view()), name='user-edit'),
    path('config/', staff_member_required(ConfigEditorView.as_view()), name='config'),
    path('staff/', staff_member_required(StaffMemberAdmin.as_view()), name='staff-admin'),
    path('staff/<int:pk>/', staff_member_required(StaffEditView.as_view()), name='staff-edit'),
    path('staff/new', staff_member_required(StaffCreateView.as_view()), name='staff-create'),
    path('staff/<int:pk>/delete', staff_member_required(StaffDeleteView.as_view()), name='staff-delete'),
    path('challenges/<int:challenge_id>/files/upload', staff_member_required(ChallengeFileChunkedUploadView.as_view()),
         name='challenge-file-upload'),
    path('challenges/<int:challenge_id>/files/upload_complete',
         staff_member_required(ChallengeFileChunkedUploadCompleteView.as_view()),
         name='challenge-file-upload-complete'),
    path('static-editor/', staff_member_required(StaticEditorList.as_view()), name='static-editor-list'),
    path('static-editor/<str:pk>/', staff_member_required(StaticEditor.as_view()), name='static-editor'),
    path('import-export/', ImportExportView.as_view(), name='import-export'),
    path('export/challenges', staff_member_required(challenge_export_view), name='challenge-export'),
    path('import-export/<log_var>/', staff_member_required(log_view), name='log-view'),
    path('export-files/<int:pk>', staff_member_required(export_download), name='export-download'),
    path('delete-export/<int:pk>', staff_member_required(ExportDeleteView.as_view()), name='export-delete'),
    path('rebalance/', staff_member_required(RebalanceView.as_view()), name='rebalance'),
]
