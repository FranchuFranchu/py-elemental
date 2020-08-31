from django.shortcuts import render
from dwebsocket.decorators import accept_websocket
from django.core import serializers
import threading
from .models import Element
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
                        if int(arg) == 0:
                            continue
                        elements.append(Element.objects.filter(sequential_number=int(arg)).first())


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



        finally:
            clients.remove(request.websocket)
            lock.release()

def index(request):
    return render(request, "index.html")