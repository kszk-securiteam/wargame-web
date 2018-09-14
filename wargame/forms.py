from django.contrib.auth.forms import UserCreationForm

from wargame.models import User


class UserRegistrationForm(UserCreationForm):
    email = None
    error_css_class = 'error'
    required_css_class = 'required'

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Remove default help text
        for field in self.Meta.fields:
            self.fields[field].help_text = None
