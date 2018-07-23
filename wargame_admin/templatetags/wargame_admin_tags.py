import os

from django.template import Library

register = Library()


@register.filter
def filename(value):
    return os.path.basename(value)
