import socket

from settings_local import *

if socket.gethostbyname(socket.getfqdn()).startswith(DEVELOPMENT_HOST) or socket.gethostbyname(socket.getfqdn()).startswith('192.168.1.'):
    from settings_development import *
else:
    from settings_production import *
