from django.forms import ModelForm

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
