from django.db import models
from django.core.exceptions import ValidationError
from re import match
from django.utils import timezone

import random, string

# Create your models here.

def color_validator(value):
    if not match(r'#[0-9a-fA-F]{6}', value):
        raise ValidationError(
            'Invalid color!',
            params = {
                "value": value
            }
        )

def color_list_validator(value):
    colors = value.split(',')
    for color in colors:
        color_validator(color) 

FG_PATTERNS = tuple([(a,a) for a in [
    "NONE",
    "STAR",
    "SQUARE",
    "CIRCLE",
    "CROSS",
    "PLUS",
]])
BG_PATTERNS = tuple([(a,a) for a in [
    "FLAT",
    "LEFT-RIGHT",
    "TOP-BOTTOM",
    "TOPLEFT-BOTTOMRIGHT",
    "TOPRIGHT-BOTTOMLEFT",
]])

class Element(models.Model):
    ingredients = models.ManyToManyField('Element', related_name="possible_recipes")
    name = models.TextField(unique=True)
    fg_colors = models.TextField(validators=[color_list_validator], null = True)
    bg_colors = models.TextField(validators=[color_list_validator], null = True)
    fg_pattern = models.CharField(choices=FG_PATTERNS, default="NONE", max_length=32)
    bg_pattern = models.CharField(choices=BG_PATTERNS, default="FLAT", max_length=32)
    default = models.BooleanField(default=False)
    password = models.CharField(max_length=32, default="")
    sequential_number = models.IntegerField(default=0, primary_key=True, unique=True)

    create_date = models.DateTimeField()
    accept_date = models.DateTimeField()
    modify_date = models.DateTimeField()
    active = models.BooleanField(default=True) 
    
    def save(self, *args, **kwargs):

        if self._state.adding:
            self.sequential_number = Element.objects.filter(active=True).count() + 1
            self.password = str(self.sequential_number) + "," + ''.join(random.choice(string.ascii_letters) for _ in range(16))
            self.accept_date = timezone.now()
            if self.create_date == None:
                self.create_date = self.accept_date

        self.modify_date = timezone.now()
        
        super().save(*args, **kwargs)
        return self

    def __str__(self):
        return f'(#{self.sequential_number}) {self.name}'

class NewElementSuggestion(models.Model):
    ingredients = models.ManyToManyField('Element', related_name="suggested_recipes")

    name = models.TextField(unique=True)
    fg_colors = models.TextField(validators=[color_list_validator], null = True)
    bg_colors = models.TextField(validators=[color_list_validator], null = True)
    fg_pattern = models.CharField(choices=FG_PATTERNS, default="NONE", max_length=32)
    bg_pattern = models.CharField(choices=BG_PATTERNS, default="FLAT", max_length=32)

    current = models.IntegerField(default=0)
    target = models.IntegerField(default=10)
    create_date = models.DateTimeField()

    voted_ips = models.TextField(default="")

    def save(self, *args, **kwargs):

        if self._state.adding:
            self.create_date = timezone.now()
        
        super().save(*args, **kwargs)
        return self

    def upvote(self):
        self.current += 1
        self.save()


    def downvote(self):
        self.current -= 1
        self.save()