from django.contrib.auth.forms import UserCreationForm

from wargame.models import User
from wargame_admin.models import Config


class UserRegistrationForm(UserCreationForm):
    error_css_class = 'error'
    required_css_class = 'required'

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'password1', 'password2', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if Config.objects.email_required():
            self.fields['email'].required = True
        else:
            del self.fields['email']

        # Remove default help text
        for field in self.fields:
            self.fields[field].help_text = None
