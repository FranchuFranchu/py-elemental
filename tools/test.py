import sys
sys.path.append(".")

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','py_elemental.settings')

import django
django.setup()

from element.models import Element, Recipe, Suggestion

from django.db.models import ManyToManyField
import dwebsocket.websocket
