from django.forms import ModelForm, Form, CharField, TextInput, FileField, FileInput, Textarea

from wargame.models import File, Challenge, User
from wargame_admin.models import StaticContent


class FileForm(ModelForm):
    class Meta:
        model = File
        fields = ['display_name', 'private', 'config_name']

    def __init__(self, *args, **kwargs):
        super(FileForm, self).__init__(*args, **kwargs)
        # Remove the blank choice
        field = self.fields['config_name']
        field.choices = field.choices[1:]


class FileUploadForm(ModelForm):
    class Meta:
        model = File
        fields = ['file', 'display_name', 'private', 'config_name']

    def __init__(self, *args, **kwargs):
        super(FileUploadForm, self).__init__(*args, **kwargs)
        # Remove the blank choice
        field = self.fields['config_name']
        field.choices = field.choices[1:]

        self.fields['file'].widget.attrs.update({'class': 'hidden'})
        self.fields['file'].label = ""


class ChallengeForm(ModelForm):
    setup = CharField(widget=Textarea)
    solution = CharField(widget=Textarea)

    class Meta:
        model = Challenge
        fields = ['title', 'description', 'short_description', 'level', 'flag_qpa', 'flag_hacktivity', 'points', 'hint',
                  'setup', 'solution']


class UserSearchForm(Form):
    name = CharField(required=False, label='', widget=TextInput(attrs={'placeholder': 'Username'}))


class UserEditForm(ModelForm):
    class Meta:
        model = User
        fields = ['is_superuser', 'hidden', 'is_active']
        labels = {
            'is_superuser': 'Admin'
        }
        help_texts = {
            'is_superuser': 'Allows the user to access the admin site and edit all objects in the django admin interface',
            'hidden': 'Hides the user from the scoreboard'
        }


class ImportForm(Form):
    file = FileField(widget=FileInput(attrs={'accept': 'application/zip'}))


class UserImportForm(Form):
    file = FileField(widget=FileInput(attrs={'accept': '.csv'}))


class StaticContentForm(ModelForm):
    class Meta:
        model = StaticContent
        fields = ['html']
        labels = {
            'html': 'Text'
        }
