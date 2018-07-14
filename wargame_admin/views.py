from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView, CreateView, DeleteView

from wargame.models import Challenge


class ChallengeListView(TemplateView):
    template_name = "wargame_admin/challenge_list.html"

    # noinspection PyMethodMayBeStatic
    def challenges(self):
        return Challenge.objects.all().order_by('level')


class ChallengeDetailsView(TemplateView):
    template_name = "wargame_admin/challenge_details.html"

    def challenge(self):
        return Challenge.objects.get(pk=self.kwargs['pk'])


challenge_form_fields = ('title', 'description', 'short_description', 'level', 'flag_qpa', 'flag_hacktivity', 'points', 'hint')


class ChallengeEditView(UpdateView):
    template_name = "wargame_admin/challenge_edit.html"
    model = Challenge
    fields = challenge_form_fields

    def get_success_url(self):
        return reverse_lazy('wargame-admin:challenge-details', kwargs={'pk': self.object.id})


class ChallengeCreateView(CreateView):
    template_name = "wargame_admin/challenge_edit.html"
    model = Challenge
    fields = challenge_form_fields

    def get_success_url(self):
        return reverse_lazy('wargame-admin:challenge-details', kwargs={'pk': self.object.id})


class ChallengeDeleteView(DeleteView):
    template_name = "wargame_admin/challenge_delete.html"
    model = Challenge

    def get_success_url(self):
        return reverse_lazy('wargame-admin:challenges')


class UserAdminView(TemplateView):
    template_name = "wargame_admin/user_admin.html"


class SubmissionAdminView(TemplateView):
    template_name = "wargame_admin/submission_admin.html"


class ConfigEditorView(TemplateView):
    template_name = "wargame_admin/config_editor.html"
