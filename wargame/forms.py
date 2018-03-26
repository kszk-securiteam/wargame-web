from registration.forms import RegistrationForm

from wargame.models import User


class UserRegistrationForm(RegistrationForm):
    email = None

    class Meta(RegistrationForm.Meta):
        model = User
        fields = ['username', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Remove default help text
        for field in self.Meta.fields:
            self.fields[field].help_text = None
