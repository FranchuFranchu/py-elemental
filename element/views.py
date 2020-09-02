from django.shortcuts import render
from dwebsocket.decorators import accept_websocket
from django.db.models import Count, F, Value
from django.core import serializers
import threading
from .models import Element, NewElementSuggestion
import json



clients = []

# Create your views here.

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
                message = message.decode()
                message = message.split(' ')
                action, args = message[0], message[1:]
                if action == 'get_default_elements':
                    
                    for element in Element.objects.filter(default=True):
                        s = serializers.serialize('json', [element])
                        request.websocket.send(f'discover_element {s}')

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

                    recipes = set(elements[0].possible_recipes.all())
                    for element in elements:
                        recipes &= set(element.possible_recipes.all())

                    if len(recipes) == 0:
                        # New element!
                        request.websocket.send(f"new_element " + ' '.join(args))

                    elif len(recipes) == 1:
                        # Already known element
                        s = serializers.serialize('json', list(recipes))
                        request.websocket.send(f'discover_element {s}')

                    elif len(recipes) > 1:
                        # Very bad thing happened! aaah panic!!
                        s = serializers.serialize('json', [list(recipes)[0]])
                        request.websocket.send(f'discover_element {s}')

                elif action == "new_element_suggestion":
                    d = json.loads(' '.join(args))

                    d["ingredients"] = filter(lambda i: i, d["ingredients"])

                    e = NewElementSuggestion.objects.create(**d["element"]["fields"])
                    e.ingredients.set(d["ingredients"])

                    e.save()
                    print(e)

                elif action == "get_vote_pending":
                    sort = args[0]

                    if sort == "latest":
                        for i in NewElementSuggestion.objects.order_by(F("create_date").asc()):
                            s = serializers.serialize('json', [i])
                            request.websocket.send(f"element_suggestion_vote {sort} {s}")

                elif action == "query_name":

                    d = json.loads(' '.join(args))

                    assert type(d) == str

                    matches = [i.name for i in Element.objects.filter(name__contains=d)[0:20]]

                    request.websocket.send(f"element_autocomplete_list {json.dumps(matches)}")

                elif action == "upvote":
                    print("test")
                    NewElementSuggestion.objects.filter(pk=int(args[0])).first().upvote()
                    for i in clients:
                        i.send("upvote " + args[0])

                elif action == "downvote":
                    NewElementSuggestion.objects.filter(pk=int(args[0])).first().downvote()
                    for i in clients:
                        i.send("downvote " + args[0])
                print(action, args)
        finally:
            clients.remove(request.websocket)
            lock.release()

def index(request):
    return render(request, "index.html")