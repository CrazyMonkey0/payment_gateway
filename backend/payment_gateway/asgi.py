import os
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'payment_gateway.settings')
django_asgi_app = get_asgi_application()

import support.routing 

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            support.routing.websocket_urlpatterns
        )
    ),
})
