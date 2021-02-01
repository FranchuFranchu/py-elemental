__all__ = [
	"get_default_elements",
	"get_element_data", 
	"get_vote_pending",
	"get_element_info",
	"combine",
	"combination_suggestion",
	"new_element_suggestion",
	"new_element",
    "query_name",
    "upvote",
    "downvote",
]

from django.db.models import Count, F, Value
from django.db import models
from . import clients
from .models import Element, Suggestion, Recipe
from django.core import serializers
from json import loads, dumps

def get_default_elements(request, data):
    
    for element in Element.objects.filter(default=True):
        s = serializers.serialize('json', [element])
        request.websocket.send(f'discover_element {s}')

def get_element_data(request, data):
    element = Element.objects.get(sequential_number=data)
    s = serializers.serialize('json', [element], fields=element.safe_fields)
    request.websocket.send(f'element_data {s}')

def combine(request, data):
    print("Combine")
    elements = []
    for arg in data:
        if not arg.strip():
            continue
        if arg == "0":
            continue
        item = Element.objects.filter(password=arg).first()

        if item:
            elements.append(item)


    if len(elements) < 2:
        print(elements)
        request.websocket.send_data("client_error", f"Invalid number of elements: {len(elements)}")
        return



    
    recipes = list(Recipe.result_of(elements))
    print(recipes)
    if len(recipes) == 0:
        # New element!
        request.websocket.send_data("new_element", data)

    elif len(recipes) == 1:
        # Already known element
        request.websocket.send_data('discover_element', [list(recipes)[0].result])

    elif len(recipes) > 1:
        # This should never happen!
        request.websocket.send_data('discover_element', [list(recipes)[0].result])

def new_element_suggestion(request, data):

    print(data)

    data["ingredients"] = list(filter(lambda i: i, data["ingredients"]))
    data["ingredients"] = ','.join([i.split(",")[0] for i in data["ingredients"]])

    valid_fields = [i.name for i in Suggestion._meta.local_fields]
    new_d = {}
    for k, v in data["element"]["fields"].items():
        if k in valid_fields:
            new_d[k] = v

    e = Suggestion.objects.create(**new_d, ingredients=data["ingredients"], edit_id=data["element"].get("pk") or 0)
        
    e.save()

def combination_suggestion(request, data):
    data["ingredients"] = list(filter(lambda i: i, data["ingredients"]))

    data["backup_ingredients"] = data["ingredients"]

    del data["ingredients"]

    e = Suggestion.objects.create(name=data["name"])

    ingredients = []

    for idx, i in enumerate(data["backup_ingredients"]):
        ingredients.append(str(Element.objects.filter(password=i).first().sequential_number))

    e.ingredients = ','.join(ingredients)

    e.save()

def get_vote_pending(request, data):
    sort = data["sort"]
    
    D = {
    	"latest": F("create_date").desc(),
    	"oldest": F("create_date").asc(),
    	"verge": F("create_date").desc(),
    	"undecided": F("create_date").asc(),
    }
    for i in Suggestion.objects.order_by(D[sort]):
    	s = dumps({"sort": sort, "element": loads(serializers.serialize('json', [i]))})
    	request.websocket.send(f'element_suggestion_vote {s}')

def query_name(request, data):
    assert type(data) == str

    matches = [i.name for i in Element.objects.filter(name__contains=data)[0:20]]

    request.websocket.send_data("element_autocomplete_list", matches)
def get_element_info(request, data):
    e_id = data["id"]
    e_pwd = data["pwd"]

    e = Element.objects.filter(sequential_number=e_id).first()

    if e is None:
        request.websocket.send_data('client_error', f'Nonexistant element!')


    elif e.password == e_pwd:
        s = serializers.serialize('json', [e])
        request.websocket.send(f'discover_element {s}')

    else:
        request.websocket.send_data(f"client_error", "Wrong element password!")

def upvote(request, data):
    print("upvote")
    a = Suggestion.objects.filter(pk=int(data)).first()
    if not a:
        return
    a.upvote(request.COOKIES.get("user_id"))
    for i in clients:
        i.send_data(f"set_vote", {"pk": int(data), "votes": a.current+a.target})

def downvote(request, data):
    print("downvote")
    a = Suggestion.objects.filter(pk=int(data)).first()
    if not a:
        return
    a.downvote(request.COOKIES.get("user_id"))
    for i in clients:
        i.send_data(f"set_vote", {"pk": int(data), "votes": a.current+a.target})
