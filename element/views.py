from django.shortcuts import render
from dwebsocket.middleware import WebSocketMiddleware
from django.conf import settings
from django.http import HttpResponse
from django.utils.decorators import decorator_from_middleware

from element import message_handlers
from django.db import models

import logging
import importlib
from django.conf import settings
from django.http import HttpResponseBadRequest
from dwebsocket.factory import WebSocketFactory

from dwebsocket.websocket import WebSocket

from traceback import format_exc

from json import dumps

def send_data(websocket, action, data):
    if isinstance(data, list) and len(data) and isinstance(data[0], models.Model):
        websocket.send(action + " " + serializers.serialize("json", data))
    else:
        websocket.send(action + " " + dumps(data))
    
WebSocket.send_data = send_data

WEBSOCKET_ACCEPT_ALL = getattr(settings, 'WEBSOCKET_ACCEPT_ALL', False)
WEBSOCKET_FACTORY_CLASS = getattr(
    settings,
    'WEBSOCKET_FACTORY_CLASS',
    'dwebsocket.backends.default.factory.WebSocketFactory',
)

logger = logging.getLogger(__name__)


class WebSocketMiddleware(object):
    def __init__(self, cls):
        pass

    @classmethod
    def process_request(cls, request):
        try:
            offset = WEBSOCKET_FACTORY_CLASS.rindex(".")
            
            factory_cls = getattr(
                importlib.import_module(WEBSOCKET_FACTORY_CLASS[:offset]),
                WEBSOCKET_FACTORY_CLASS[offset+1:]
            )
            request.websocket = factory_cls(request).create_websocket()
        except ValueError as e:
            logger.debug(e)
            request.websocket = None
            request.is_websocket = lambda: False
            return HttpResponseBadRequest()
        if request.websocket is None:
            request.is_websocket = lambda: False
        else:
            request.is_websocket = lambda: True

    @classmethod
    def process_view(cls, request, view_func, view_args, view_kwargs):
        # open websocket if its an accepted request
        if request.is_websocket():
            # deny websocket request if view can't handle websocket
            if not WEBSOCKET_ACCEPT_ALL and \
                not getattr(view_func, 'accept_websocket', False):
                return HttpResponseBadRequest()
            # everything is fine .. so prepare connection by sending handshake
            request.websocket.accept_connection()
        elif getattr(view_func, 'require_websocket', False):
            # websocket was required but not provided
            return HttpResponseBadRequest()

    @classmethod
    def process_response(cls, request, response):
        if request.is_websocket():
            request.websocket.close()
        return response

    @classmethod
    def process_exception(cls, request, exception):
        if request.is_websocket():
            request.websocket.close()


from django.db.models import Count, F, Value
from django.core import serializers
import threading
from uuid import uuid5
from .models import Element, Suggestion, Recipe
import random
import string
from time import time
import json
from . import clients

# Create your views here.


WEBSOCKET_MIDDLEWARE_INSTALLED = False

def _setup_websocket(func):
    from functools import wraps
    @wraps(func)
    def new_func(request, *args, **kwargs):
        response = func(request, *args, **kwargs)
        if response is None and request.is_websocket():
            response =  HttpResponse()
            response.__len__ = lambda : 0
            return response
        return response
    if not WEBSOCKET_MIDDLEWARE_INSTALLED:
        decorator = decorator_from_middleware(WebSocketMiddleware)
        new_func = decorator(new_func)
    return new_func


def accept_websocket(func):
    func.accept_websocket = True
    func.require_websocket = getattr(func, 'require_websocket', False)
    func = _setup_websocket(func)
    return func


@accept_websocket
def main_socket(request):
    if request.is_websocket:
        lock = threading.RLock()
        try:
            lock.acquire()
            clients.append(request.websocket)
            for message in request.websocket:
                if not message:
                    break
                code, args = message.decode('utf-8').split(' ', 1)
                if code in message_handlers.__all__:
                    try:
                        message_handlers.__dict__[code](request, json.loads(args))
                    except Exception as e:
                        print("Client triggered exception:")
                        print(code, args)
                        request.websocket.send_data("server_error", format_exc())
                else:
                    print("Unrecognized websocket action:", code)

        finally:
            clients.remove(request.websocket)
            lock.release()

def index(request):
    response = render(request, "index.html")

    if not request.COOKIES.get("user_id"):
        response.set_cookie("user_id", ''.join(random.choice(string.ascii_letters) for _ in range(40)) + str(time()))

    return response