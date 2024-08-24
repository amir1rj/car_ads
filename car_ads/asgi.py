import os
import django
django.setup()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "car_ads.settings")
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from chat.routing import websocket_urlpatterns
from channels.security.websocket import OriginValidator




django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": OriginValidator(
            AuthMiddlewareStack(
                URLRouter(websocket_urlpatterns)
            ),
            ['*']
        ),
    }
)