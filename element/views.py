from django.shortcuts import render
from dwebsocket.middleware import WebSocketMiddleware
from django.conf import settings
from django.http import HttpResponse
from django.utils.decorators import decorator_from_middleware

import logging
import importlib
from django.conf import settings
from django.http import HttpResponseBadRequest
from dwebsocket.factory import WebSocketFactory


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
    print("connect " + str(request))
    print(request.COOKIES)
    if request.is_websocket:
        lock = threading.RLock()
        try:
            lock.acquire()
            clients.append(request.websocket)
            for message in request.websocket:
                if not message:
                    break
                message = message.decode()
                message = message.split(' ')
                action, args = message[0], message[1:]
                if action == 'get_default_elements':
                    
                    for element in Element.objects.filter(default=True):
                        s = serializers.serialize('json', [element])
                        request.websocket.send(f'discover_element {s}')

                elif action == "get_element_data":
                    pk = int(args[0])
                    element = Element.objects.get(sequential_number=args[0])
                    s = serializers.serialize('json', [element], fields=element.safe_fields)
                    request.websocket.send(f'element_data {s}')

                elif action == 'combine':
                    elements = []
                    for arg in args:
                        if not arg.strip():
                            continue
                        if arg == "0":
                            continue
                        item = Element.objects.filter(password=arg).first()

                        if item:
                            elements.append(item)


                    if len(elements) < 2:
                        print(elements)
                        request.websocket.send(f"error Invalid number of elements: {len(elements)}")
                        continue



                    
                    recipes = list(Recipe.objects.filter(ingredients=','.join([str(i.sequential_number) for i in elements])))
                    print(recipes)
                    if len(recipes) == 0:
                        # New element!
                        request.websocket.send(f"new_element " + ' '.join(args))

                    elif len(recipes) == 1:
                        # Already known element
                        s = serializers.serialize('json', [list(recipes)[0].result])
                        print(s)
                        request.websocket.send(f'discover_element {s}')

                    elif len(recipes) > 1:
                        # Very bad thing happened! aaah panic!!
                        s = serializers.serialize('json', [list(recipes)[0]])
                        request.websocket.send(f'discover_element {s}')

                elif action == "new_element_suggestion":
                    d = json.loads(' '.join(args))

                    print(d)

                    d["ingredients"] = list(filter(lambda i: i, d["ingredients"]))
                    d["ingredients"] = ','.join([i.split(",")[0] for i in d["ingredients"]])
                    print(d["ingredients"])

                    e = Suggestion.objects.create(**d["element"]["fields"], ingredients=d["ingredients"])
                    e.save()

                elif action == "combination_suggestion":
                    d = json.loads(' '.join(args))

                    print(d)

                    d["ingredients"] = list(filter(lambda i: i, d["ingredients"]))

                    d["backup_ingredients"] = d["ingredients"]

                    del d["ingredients"]

                    e = Suggestion.objects.create(name=d["name"])

                    for idx, i in enumerate(d["backup_ingredients"]):
                        e.ingredients.add(Element.objects.filter(password=i).first())

                    e.save()

                elif action == "get_vote_pending":
                    sort = args[0]

                    if sort == "latest":
                        for i in Suggestion.objects.order_by(F("create_date").desc()):
                            s = serializers.serialize('json', [i])
                            request.websocket.send(f"element_suggestion_vote {sort} {s}")

                    elif sort == "oldest":
                        for i in Suggestion.objects.order_by(F("create_date").asc()):
                            s = serializers.serialize('json', [i])
                            request.websocket.send(f"element_suggestion_vote {sort} {s}")

                    elif sort == "verge":
                        end = 10

                        for i in Suggestion.objects.order_by(F("verge").desc()):
                            s = serializers.serialize('json', [i])
                            request.websocket.send(f"element_suggestion_vote {sort} {s}")

                    elif sort == "undecided":
                        end = 10

                        for i in Suggestion.objects.order_by(F("verge").asc()):
                            s = serializers.serialize('json', [i])
                            request.websocket.send(f"element_suggestion_vote {sort} {s}")

                elif action == "query_name":

                    d = json.loads(' '.join(args))

                    assert type(d) == str

                    matches = [i.name for i in Element.objects.filter(name__contains=d)[0:20]]

                    request.websocket.send(f"element_autocomplete_list {json.dumps(matches)}")
                elif action == "get_element_info":
                    e_id = int(args[0])
                    e_pwd = args[1]

                    e = Element.objects.filter(sequential_number=e_id).first()

                    if e is None:
                        request.websocket.send(f'error Nonexistant element!')


                    elif e.password == e_pwd:
                        s = serializers.serialize('json', [e])
                        request.websocket.send(f'discover_element {s}')

                    else:
                        request.websocket.send(f"error Wrong password!")
                elif action == "upvote":
                    print("test")
                    a = Suggestion.objects.filter(pk=int(args[0])).first()
                    if not a:
                        continue
                    a.upvote(request.COOKIES.get("user_id"))
                    for i in clients:
                        i.send(f"set_vote {args[0]} {a.current}")

                elif action == "downvote":
                    a = Suggestion.objects.filter(pk=int(args[0])).first()
                    if not a:
                        continue
                    a.downvote(request.COOKIES.get("user_id"))
                    for i in clients:
                        i.send(f"set_vote {args[0]} {a.current}")
                print(action, args)
        finally:
            clients.remove(request.websocket)
            lock.release()

def index(request):
    response = render(request, "index.html")

    if not request.COOKIES.get("user_id"):
        response.set_cookie("user_id", ''.join(random.choice(string.ascii_letters) for _ in range(40)) + str(time()))

    return response