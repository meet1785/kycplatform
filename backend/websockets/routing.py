from django.urls import path
from websockets.consumers import KYCConsumer

websocket_urlpatterns = [
    path("ws/kyc/", KYCConsumer.as_asgi()),
]
