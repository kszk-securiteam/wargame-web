from django.template import Library
from django.utils.safestring import mark_safe
from markdownx.utils import markdownify

register = Library()


@register.filter
def markdown(value):
    return mark_safe(markdownify(value))
