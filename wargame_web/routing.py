from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path

from wargame_admin.consumers import LogConsumer

application = ProtocolTypeRouter({
    'websocket': AllowedHostsOriginValidator(AuthMiddlewareStack(
        URLRouter([
            path('ws/log/<log_var>/', LogConsumer)
        ])))
})
