import os

from django.template import Library

from utils.challenge_import import MessageType

register = Library()


@register.simple_tag
def submission_name(view, userchallenge):
    return view.get_userchallenge_text(userchallenge)


@register.simple_tag
def append_url(base_url, view, userchallenge):
    return base_url + view.get_userchallenge_id_string(userchallenge)


def get_messagetype_class(instance):
    return {
        MessageType.ERROR: "text-danger",
        MessageType.WARNING: "text-warning",
        MessageType.INFO: "text-info",
        MessageType.SUCCESS: "text-success"
    }.get(instance, "")


@register.simple_tag
def render_message(message):
    message_type, string = message
    return F'<code class="{get_messagetype_class(message_type)}">{string}</code>'
