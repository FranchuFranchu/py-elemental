from django.db.models import Model, IntegerField, BooleanField, ManyToManyField, ForeignKey, SET_NULL, TextField
from element.models import Element, Recipe

class DiscordUser(Model):
    id = IntegerField(primary_key=True)
    has_elements = ManyToManyField(Element)
    last_ingredients = TextField(null=True)

class DiscordChannel(Model):
    id = IntegerField(primary_key=True)    
    play_channel = BooleanField(default=False)
    vote_channel = BooleanField(default=False)
