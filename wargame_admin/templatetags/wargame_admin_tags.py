import os

from django.template import Library

register = Library()


@register.filter
def filename(value):
    return os.path.basename(value)


@register.simple_tag
def submission_name(view, userchallenge):
    return view.get_userchallenge_text(userchallenge)


@register.simple_tag
def append_url(base_url, view, userchallenge):
    return base_url + view.get_userchallenge_id_string(userchallenge)
