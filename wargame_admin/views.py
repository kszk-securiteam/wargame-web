import os
from abc import ABCMeta, abstractmethod

from chunked_upload.constants import http_status
from chunked_upload.exceptions import ChunkedUploadError
from chunked_upload.views import ChunkedUploadView, ChunkedUploadCompleteView
from django.contrib import messages
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView, CreateView, DeleteView
from search_views.views import SearchListView

from utils.challenge_import import do_challenge_import
from utils.user_import import do_user_import
from utils.serve_file import serve_file
from utils.export_challenges import export_challenges
from wargame.models import Challenge, File, UserChallenge, User, StaffMember
from wargame_admin.filters import UserFilter
from wargame_admin.forms import ChallengeForm, FileForm, FileUploadForm, UserSearchForm, UserEditForm, ImportForm, \
    UserImportForm, StaticContentForm
from wargame_admin.models import Config, ChallengeFileChunkedUpload, StaticContent


class ChallengeListView(TemplateView):
    template_name = "wargame_admin/challenge_list.html"

    # noinspection PyMethodMayBeStatic
    def challenges(self):
        return Challenge.objects.all().order_by('level')


class ChallengeDetailsView(TemplateView):
    template_name = "wargame_admin/challenge_details.html"

    def challenge(self):
        return Challenge.objects.get(pk=self.kwargs['pk'])

    def qpa_files(self):
        return self.challenge().files.filter(config_name='qpa').all()

    def hacktivity_files(self):
        return self.challenge().files.filter(config_name='hacktivity').all()

    def tag_list(self):
        return ', '.join(self.challenge().tags.names())


class ChallengeEditView(UpdateView):
    template_name = "wargame_admin/edit_form.html"
    model = Challenge
    form_class = ChallengeForm

    def get_success_url(self):
        messages.success(self.request, "Challenge saved.")
        return reverse_lazy('wargame-admin:challenge-details', kwargs={'pk': self.object.id})


class ChallengeCreateView(CreateView):
    template_name = "wargame_admin/edit_form.html"
    model = Challenge
    form_class = ChallengeForm

    def get_success_url(self):
        messages.success(self.request, "Challenge created.")
        return reverse_lazy('wargame-admin:challenge-details', kwargs={'pk': self.object.id})


class ChallengeDeleteView(DeleteView):
    template_name = "wargame_admin/challenge_delete.html"
    model = Challenge

    def get_success_url(self):
        messages.success(self.request, "Challenge deleted.")
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
        formset = self.file_form_set(request.POST, request.FILES, instance=self.challenge())
        if formset.is_valid():
            formset.save()
            messages.success(self.request, "Files saved.")

        return HttpResponseRedirect(self.request.path_info)  # Redirect to the same page


class ChallengeFileDeleteView(DeleteView):
    template_name = 'wargame_admin/challenge_file_delete.html'
    model = File

    def get_success_url(self):
        messages.success(self.request, "File deleted.")
        return reverse_lazy('wargame-admin:challenge-files', kwargs={'pk': self.object.challenge.id})


class UserAdminView(SearchListView):
    template_name = "wargame_admin/user_admin.html"
    model = User
    paginate_by = 300
    form_class = UserSearchForm
    filter_class = UserFilter

    # noinspection PyMethodMayBeStatic
    def users(self):
        return User.objects.order_by('-is_staff').all()


class SubmissionsView(TemplateView, metaclass=ABCMeta):
    template_name = "wargame_admin/submissions.html"

    @abstractmethod
    def list(self):
        pass

    def selected_id(self):
        arg = self.request.GET.get('id')
        if arg is None:
            return None
        return int(arg)

    @abstractmethod
    def userchallenges(self):
        pass

    @abstractmethod
    def get_userchallenge_text(self, userchallenge):
        pass

    @abstractmethod
    def reset_hint_url(self):
        pass

    @abstractmethod
    def clear_submissions_url(self):
        pass

    @abstractmethod
    def get_userchallenge_id_string(self, userchallenge):
        pass


class ChallengeSubmissions(SubmissionsView):

    # noinspection PyMethodMayBeStatic
    def list(self):
        return Challenge.objects.values_list('id', 'title').all()

    def userchallenges(self):
        return UserChallenge.objects.filter(challenge_id=self.selected_id()).all()

    # noinspection PyMethodMayBeStatic
    def get_userchallenge_text(self, userchallenge):
        return userchallenge.user.username

    def reset_hint_url(self):
        return f"{reverse_lazy('wargame-admin:submission-reset-hint')}?return=challenges&challenge_id={self.selected_id()}"

    def clear_submissions_url(self):
        return f"{reverse_lazy('wargame-admin:submission-clear')}?return=challenges&challenge_id={self.selected_id()}"

    # noinspection PyMethodMayBeStatic
    def get_userchallenge_id_string(self, userchallenge):
        return f"&user_id={userchallenge.user_id}"


class UserSubmissions(SubmissionsView):
    template_name = "wargame_admin/submissions.html"

    # noinspection PyMethodMayBeStatic
    def list(self):
        return User.objects.values_list('id', 'username').all()

    def userchallenges(self):
        return UserChallenge.objects.filter(user_id=self.selected_id()).all()

    # noinspection PyMethodMayBeStatic
    def get_userchallenge_text(self, userchallenge):
        return userchallenge.challenge.title

    def reset_hint_url(self):
        return f"{reverse_lazy('wargame-admin:submission-reset-hint')}?return=users&user_id={self.selected_id()}"

    def clear_submissions_url(self):
        return f"{reverse_lazy('wargame-admin:submission-clear')}?return=users&user_id={self.selected_id()}"

    # noinspection PyMethodMayBeStatic
    def get_userchallenge_id_string(self, userchallenge):
        return f"&challenge_id={userchallenge.challenge_id}"


class SubmissionActionView(TemplateView, metaclass=ABCMeta):
    template_name = "wargame_admin/submissions_action.html"

    def user(self):
        user_id = self.request.GET.get("user_id")
        if user_id is None:
            return None
        return User.objects.get(pk=user_id)

    def challenge(self):
        challenge_id = self.request.GET.get("challenge_id")
        if challenge_id is None:
            return None
        return Challenge.objects.get(pk=challenge_id)

    def return_url(self):
        if self.request.GET.get('return') == 'challenges':
            return f"{reverse_lazy('wargame-admin:challenge-submissions')}?id={self.challenge().id.__str__()}"
        if self.request.GET.get('return') == 'users':
            return f"{reverse_lazy('wargame-admin:user-submissions')}?id={self.user().id.__str__()}"

    def userchallenges(self):
        if self.challenge() is None:
            return self.user().userchallenge_set.all()
        if self.user() is None:
            return self.challenge().userchallenge_set.all()
        return [UserChallenge.get_or_create(self.user(), self.challenge())]

    def get(self, request, *args, **kwargs):
        if (self.user() is None and self.challenge() is None) or self.request.GET.get('return') is None:
            return HttpResponseBadRequest()
        return super().get(request, *args, **kwargs)

    @abstractmethod
    def action_string(self):
        pass

    @abstractmethod
    def do_action(self, userchallenge):
        pass

    def post(self, request, *args, **kwargs):
        for userchallenge in self.userchallenges():
            self.do_action(userchallenge)
            if not userchallenge.hint_used and not userchallenge.submission_set.exists():
                userchallenge.delete()
            else:
                userchallenge.save()
        return HttpResponseRedirect(self.return_url())


class ResetHintsView(SubmissionActionView):
    def do_action(self, userchallenge):
        userchallenge.hint_used = False
        messages.success(self.request, "Hints reset.")

    def action_string(self):
        return "reset hints"


class ClearSubmissionsView(SubmissionActionView):
    def do_action(self, userchallenge):
        userchallenge.submission_set.all().delete()
        messages.success(self.request, "Submissions cleared.")

    def action_string(self):
        return "clear submissions"


class UserEdit(UpdateView):
    template_name = "wargame_admin/user_edit.html"
    model = User
    form_class = UserEditForm

    def get_success_url(self):
        self.object.is_staff = self.object.is_superuser
        self.object.save()
        messages.success(self.request, "User saved.")
        return reverse_lazy('wargame-admin:users')


class ConfigEditorView(TemplateView):
    template_name = "wargame_admin/config_editor.html"

    # noinspection PyMethodMayBeStatic
    def configs(self):
        return Config.objects.all()

    def post(self, request, *args, **kwargs):
        for key, value in request.POST.dict().items():
            if key == 'csrfmiddlewaretoken':
                continue
            config = Config.objects.get(key=key)
            config.value = value
            config.save()
        messages.success(self.request, "Configuration saved.")
        return HttpResponseRedirect(self.request.path_info)


class StaffMemberAdmin(TemplateView):
    template_name = 'wargame_admin/staff_admin.html'

    # noinspection PyMethodMayBeStatic
    def staff_members(self):
        return StaffMember.objects.all()


class StaffEditView(UpdateView):
    template_name = "wargame_admin/edit_form.html"
    fields = ('name',)
    model = StaffMember

    def get_success_url(self):
        messages.success(self.request, "Staff member saved.")
        return reverse_lazy('wargame-admin:staff-admin')


class StaffCreateView(CreateView):
    template_name = "wargame_admin/edit_form.html"
    fields = ('name',)
    model = StaffMember

    def get_success_url(self):
        messages.success(self.request, "Staff member created.")
        return reverse_lazy('wargame-admin:staff-admin')


class StaffDeleteView(DeleteView):
    template_name = "wargame_admin/staff_delete.html"
    model = StaffMember

    def get_success_url(self):
        messages.success(self.request, "Staff member deleted.")
        return reverse_lazy('wargame-admin:staff-admin')


class ImportView(TemplateView):
    template_name = "wargame_admin/import.html"
    import_messages = []

    def messages(self):
        return self.import_messages

    def form(self):
        return ImportForm()

    def post(self, request, *args, **kwargs):
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            self.import_messages = do_challenge_import(form.files['file'])

        return super().get(request, *args, **kwargs)


class UserImportView(TemplateView):
    template_name = "wargame_admin/user_import.html"

    # noinspection PyMethodMayBeStatic
    def form(self):
        return UserImportForm()

    def post(self, request, *args, **kwargs):
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            do_user_import(form.files['file'])

        return HttpResponseRedirect(reverse_lazy('wargame-admin:users'))


def challenge_export_view(request):
    file_name = export_challenges()
    return serve_file(request, file_name)


class ChallengeFileChunkedUploadView(ChunkedUploadView):
    model = ChallengeFileChunkedUpload
    field_name = "file"

    def check_permissions(self, request):
        if not request.user.is_superuser:
            raise ChunkedUploadError(status=http_status.HTTP_403_FORBIDDEN)


class ChallengeFileChunkedUploadCompleteView(ChunkedUploadCompleteView):
    model = ChallengeFileChunkedUpload

    def check_permissions(self, request):
        if not request.user.is_superuser:
            raise ChunkedUploadError(status=http_status.HTTP_403_FORBIDDEN)

    def on_completion(self, uploaded_file, request):
        form = FileUploadForm(request.POST, {'file': uploaded_file})
        if form.is_valid():
            file = form.save(commit=False)
            file.challenge_id = self.kwargs['challenge_id']
            file.filename = uploaded_file.name
            file.save()
            messages.success(request, "File uploaded.")
        else:
            messages.error(request, "Error uploading file:" + form.errors)


class StaticEditorList(TemplateView):
    template_name = "wargame_admin/static_editor.html"

    def content_list(self):
        return StaticContent.objects.values('key', 'display_name')


class StaticEditor(UpdateView):
    template_name = "wargame_admin/code_edit_form.html"
    form_class = StaticContentForm
    model = StaticContent

    def get_success_url(self):
        messages.success(self.request, "Content saved.")
        return reverse_lazy('wargame-admin:static-editor-list')
