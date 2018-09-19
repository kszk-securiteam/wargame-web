from django.forms import ModelForm, Form, CharField, TextInput, FileField, FileInput

from wargame.models import File, Challenge, User


class FileForm(ModelForm):
    class Meta:
        model = File
        fields = ['display_name', 'private']


class FileUploadForm(ModelForm):
    class Meta:
        model = File
        fields = ['file', 'display_name', 'private']


class ChallengeForm(ModelForm):
    class Meta:
        model = Challenge
        fields = ['title', 'description', 'short_description', 'level', 'flag_qpa', 'flag_hacktivity', 'points', 'hint']


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
