from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages

from wargame_admin.models import Config


class DisableSiteMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not Config.objects.wargame_active():
            if request.path.startswith("/challenges") or (
                    request.path.startswith("/challenge-files") and not request.user.is_staff):

                messages.warning(request, "The wargame is not running, you can't view the challenges.")
                return HttpResponseRedirect(reverse_lazy("scoreboard"))

        return self.get_response(request)
