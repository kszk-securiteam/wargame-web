from django.forms import TextInput
from django_filters import FilterSet, CharFilter

from wargame.models import User


class UserFilter(FilterSet):
    username = CharFilter(label="", lookup_expr="contains", widget=TextInput(attrs={"placeholder": "Username"}))

    class Meta:
        model = User
        fields = {}
