from django.template import Library
from django.utils.safestring import mark_safe
from markdownx.utils import markdownify

from wargame_admin.models import Config

register = Library()


@register.filter
def markdown(value):
    return mark_safe(markdownify(value))


@register.filter
def qpa_mul(value):
    return int(round(value * Config.objects.qpa_points_multiplier(), -1))
