from django.views.generic import TemplateView

from wargame.models import Challenge


class ChallengeListView(TemplateView):
    template_name = "wargame_admin/challenge_list.html"

    def challenges(self):
        return Challenge.objects.all().order_by('level')


class ChallengeDetailsView(TemplateView):
    template_name = "wargame_admin/challenge_details.html"

    def challenge(self):
        return Challenge.objects.get(pk=self.kwargs['id'])


class ChallengeEditView(TemplateView):
    template_name = "wargame_admin/challenge_edit.html"


class UserAdminView(TemplateView):
    template_name = "wargame_admin/user_admin.html"


class SubmissionAdminView(TemplateView):
    template_name = "wargame_admin/submission_admin.html"


class ConfigEditorView(TemplateView):
    template_name = "wargame_admin/config_editor.html"
