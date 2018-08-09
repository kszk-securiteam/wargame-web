from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView, CreateView, DeleteView

from wargame_admin.forms import ChallengeForm, FileForm, FileUploadForm
from wargame.models import Challenge, File, Submission, UserChallenge, User


class ChallengeListView(TemplateView):
    template_name = "wargame_admin/challenge_list.html"

    # noinspection PyMethodMayBeStatic
    def challenges(self):
        return Challenge.objects.all().order_by('level')


class ChallengeDetailsView(TemplateView):
    template_name = "wargame_admin/challenge_details.html"

    def challenge(self):
        return Challenge.objects.get(pk=self.kwargs['pk'])


class ChallengeEditView(UpdateView):
    template_name = "wargame_admin/challenge_edit.html"
    model = Challenge
    form_class = ChallengeForm

    def get_success_url(self):
        return reverse_lazy('wargame-admin:challenge-details', kwargs={'pk': self.object.id})


class ChallengeCreateView(CreateView):
    template_name = "wargame_admin/challenge_edit.html"
    model = Challenge
    form_class = ChallengeForm

    def get_success_url(self):
        return reverse_lazy('wargame-admin:challenge-details', kwargs={'pk': self.object.id})


class ChallengeDeleteView(DeleteView):
    template_name = "wargame_admin/challenge_delete.html"
    model = Challenge

    def get_success_url(self):
        return reverse_lazy('wargame-admin:challenges')


class ChallengeFilesView(TemplateView):
    template_name = "wargame_admin/challenge_files.html"
    file_form_set = inlineformset_factory(Challenge, File, form=FileForm, extra=0, can_delete=False)

    def challenge(self):
        return Challenge.objects.get(pk=self.kwargs['pk'])

    # noinspection PyMethodMayBeStatic
    def file_upload_form(self):
        return FileUploadForm()

    def formset(self):
        return self.file_form_set(instance=self.challenge())

    def post(self, request, *args, **kwargs):
        # If a new file was uploaded
        if request.FILES:
            form = FileUploadForm(request.POST, request.FILES)
            if form.is_valid():
                file = form.save(commit=False)
                file.challenge_id = kwargs['pk']
                file.save()

        # If the set of existing files was edited
        else:
            formset = self.file_form_set(request.POST, request.FILES, instance=self.challenge())
            if formset.is_valid():
                formset.save()

        return HttpResponseRedirect(self.request.path_info)  # Redirect to the same page


class ChallengeFileDeleteView(DeleteView):
    template_name = 'wargame_admin/challenge_file_delete.html'
    model = File

    def get_success_url(self):
        return reverse_lazy('wargame-admin:challenge-files', kwargs={'pk': self.object.challenge.id})


class UserAdminView(TemplateView):
    template_name = "wargame_admin/user_admin.html"

    # noinspection PyMethodMayBeStatic
    def users(self):
        return User.objects.order_by('-is_staff').all()


class ChallengeSubmissions(TemplateView):
    template_name = "wargame_admin/submissions.html"

    # noinspection PyMethodMayBeStatic
    def list(self):
        return Challenge.objects.values_list('id', 'title').all()

    def selected_id(self):
        return int(self.request.GET['id'])

    def userchallenges(self):
        return UserChallenge.objects.filter(challenge_id=self.selected_id()).all()

    # noinspection PyMethodMayBeStatic
    def get_userchallenge_text(self, userchallenge):
        return userchallenge.challenge.title


class UserSubmissions(TemplateView):
    template_name = "wargame_admin/submissions.html"

    # noinspection PyMethodMayBeStatic
    def list(self):
        return User.objects.values_list('id', 'username').all()

    def selected_id(self):
        return int(self.request.GET['id'])

    def userchallenges(self):
        return UserChallenge.objects.filter(user_id=self.selected_id()).all()

    # noinspection PyMethodMayBeStatic
    def get_userchallenge_text(self, userchallenge):
        return userchallenge.user.username


class ConfigEditorView(TemplateView):
    template_name = "wargame_admin/config_editor.html"
