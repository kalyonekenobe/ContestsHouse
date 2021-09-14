import base64
from mainapp.models import *


def get_client_ip(request):
    x_forwared_for = request.META.get('HTTP_X_FORWARED_FOR')
    if x_forwared_for:
        ip = x_forwared_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def encode_value(value, encoding='ascii'):
    return base64.b64encode(str(value).encode(encoding)).decode(encoding)


def decode_value(value, encoding='ascii'):
    return base64.b64decode(str(value).encode(encoding)).decode(encoding)

