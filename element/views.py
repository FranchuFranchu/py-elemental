from django.shortcuts import render
from dwebsocket.decorators import accept_websocket
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