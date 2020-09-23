import sys
sys.path.append(".")

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','py_elemental.settings')

import django
django.setup()

from element.models import Element, Recipe, Suggestion

from django.db.models import ManyToManyField
import dwebsocket.websocket

Recipe.objects.all().delete()
Suggestion.objects.all().delete()

Element.objects.all().delete()

e = Element.objects.create(
    name = "Water",
    default = True,
    bg_colors = "#002bad,#FFFFFF",
    fg_colors = "#000000,#000000",
)
e.save()

e = Element.objects.create(
    name = "Earth",
    default = True,
    bg_colors = "#ba8e00,#FFFFFF",
    fg_colors = "#000000,#000000",
)
e.save()

e = Element.objects.create(
    name = "Fire",
    default = True,
    bg_colors = "#ca3b02,#FFFFFF",
    fg_colors = "#000000,#000000",
)
e.save()

e = Element.objects.create(
    name = "Air",
    default = True,
    bg_colors = "#fefefe,#FFFFFF",
    fg_colors = "#000000,#000000",
)
e.save()