from channels.routing import route

from .consumers import webservice_add, webservice_disconnect


channel_routing = [
     route("websocket.connect", webservice_add),
     route("websocket.disconnect", webservice_disconnect),
]
