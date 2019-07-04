from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.safestring import mark_safe

from wargame_admin.models import Config, StaticContent


class DisableSiteMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not Config.objects.wargame_active():
            if request.path.startswith("/challenges") or (
                request.path.startswith("/challenge-files") and not request.user.is_staff
            ):

                messages.warning(request, "The wargame is not running, you can't view the challenges.")
                return HttpResponseRedirect(reverse_lazy("scoreboard"))

        return self.get_response(request)


class RequireEmailMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            Config.objects.email_required()
            and request.user.is_authenticated
            and not request.user.email
            and not request.path.startswith("/user/set-email")
        ):

            text = StaticContent.objects.get(key="email_notification").html

            storage = messages.get_messages(request)
            for message in storage:
                if message.message == text:
                    storage.used = False
                    return self.get_response(request)

            storage.used = False

            messages.warning(request, mark_safe(text))

        return self.get_response(request)
