"""
Serves files using Django in debug mode or nginx in production. file_dir is the path of the file relative to the media
url/root defined in settings. In production, an nginx alias is required from the media url to a location on the file
system.
"""
from os.path import join
from django.http import HttpResponse
from django.views.static import serve
from wargame_web.settings import base as settings


def serve_file(request, file_dir, file_name):
    if not settings.DEBUG:
        response = HttpResponse()
        response['X-Accel-Redirect'] = join(settings.MEDIA_URL, file_dir, file_name)
    else:
        response = serve(request, join("/", file_dir, file_name), settings.MEDIA_ROOT)

    response["Content-Disposition"] = F"attachment; filename={file_name}"
    return response
