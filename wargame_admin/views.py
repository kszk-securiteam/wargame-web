from django.views.generic import TemplateView


class ChallengeListView(TemplateView):
    template_name = "wargame_admin/challenge_list.html"


class ChallengeDetailsView(TemplateView):
    template_name = "wargame/challenge_details.html"


class ChallengeEditView(TemplateView):
    template_name = "wargame_admin/challenge_edit.html"


class UserAdminView(TemplateView):
    template_name = "wargame_admin/user_admin.html"


class SubmissionAdminView(TemplateView):
    template_name = "wargame_admin/submission_admin.html"


class ConfigEditorView(TemplateView):
    template_name = "wargame_admin/config_editor.html"
