from django.forms import ModelForm, Form, CharField, TextInput

from wargame.models import File, Challenge


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
