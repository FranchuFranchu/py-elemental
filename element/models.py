from django.db import models
from django.core.exceptions import ValidationError
from re import match
from django.utils import timezone
from . import clients

import json

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

class IngredientMixin():
    """
    def set_ingredients(self, x):
        self.ingredients = ','.join([i.sequential_number for i in x])
        

    def get_ingredients(self):
        return [Element.objects.filter(sequential_number=int(i)) for i in self.ingredients.split(',')]
    """ 

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

class Recipe(models.Model, IngredientMixin):
    
    ingredients = models.TextField()
    result = models.ForeignKey('Element', related_name="producing_recipes", on_delete=models.CASCADE)
    create_date = models.DateTimeField()
    accept_date = models.DateTimeField()
    modify_date = models.DateTimeField()

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.accept_date = timezone.now()

        self.modify_date = timezone.now()
        
        super().save(*args, **kwargs)
        return self


class Element(models.Model):
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

    @property
    def safe_fields(self):
        
        fields = type(self)._meta.local_fields

        return list(filter(lambda i: i != "password", [i.name for i in fields]))
    
    def save(self, *args, **kwargs):
        print(self.name)
        if self._state.adding:
            self.sequential_number = Element.objects.filter().count() + 1
            self.password = str(self.sequential_number) + "," + ''.join(random.choice(string.ascii_letters) for _ in range(16))
            self.accept_date = timezone.now()
            if self.create_date == None:
                self.create_date = self.accept_date

        self.modify_date = timezone.now()
        
        super().save(*args, **kwargs)
        return self

    def __str__(self):
        return f'(#{self.sequential_number}) {self.name}'

class Suggestion(models.Model, IngredientMixin):

    ingredients = models.TextField()
    name = models.TextField()
    fg_colors = models.TextField(validators=[color_list_validator], null = True)
    bg_colors = models.TextField(validators=[color_list_validator], null = True)
    fg_pattern = models.CharField(choices=FG_PATTERNS, default="NONE", max_length=32, null=True)
    bg_pattern = models.CharField(choices=BG_PATTERNS, default="FLAT", max_length=32, null=True)

    current = models.IntegerField(default=0)
    target = models.IntegerField(default=1)
    verge = models.IntegerField(default=1)
    create_date = models.DateTimeField()

    suggestion_type = models.CharField(max_length=10)

    voters = models.TextField(default='{"up":[],"down":[]}')

    voted_ips = models.TextField(default="")

    def set_voters(self, x):
        self.voters = json.dumps(x)

    def get_voters(self):
        return json.loads(self.voters)

    def get_suggestion_type(self):
        if self.ingredients == "":
            return "edit"
        elif Element.objects.filter(name=self.name).first():
            return "combination"
        else:
            return "new"

    def result_accept(self):
        
        d = {k:v for k, v in self.__dict__.items()}
        del d["voted_ips"]
        del d["current"]
        del d["_state"]
        del d["id"]
        del d["verge"]
        del d["target"]
        del d["voters"]
        del d["ingredients"]
        del d["suggestion_type"]

        for i in clients:
            i.send("vote_accept " + str(self.pk))

        print(d)

        if bool(self.bg_colors) or bool(self.fg_colors):
            e = Element.objects.create(**d)
            e.save()

        r = Recipe.objects.create(result=e, create_date=self.create_date, ingredients=self.ingredients)

        self.delete()

    def result_reject(self):
        for i in clients:
            i.send("vote_reject " + str(self.pk))
        self.delete()

    def save(self, *args, **kwargs):

        if self._state.adding:
            self.create_date = timezone.now()

        self.verge = abs(self.target-self.current)
        self.suggestion_type = self.get_suggestion_type()
        
        super().save(*args, **kwargs)
        return self

    def upvote(self, uid):
        voters = self.get_voters()

        if uid in voters["down"]:
            voters["down"].remove(uid)
            self.set_voters(voters)

        if uid not in voters["up"]:

            voters["up"].append(uid)
            self.set_voters(voters)

            self.current += 1
            if self.current >= self.target:
                self.result_accept()
            else:
                self.save()


    def downvote(self, uid):
        voters = self.get_voters()

        if uid in voters["up"]:
            voters["up"].remove(uid)
            self.set_voters(voters)

        if uid not in voters["down"]:

            voters["down"].append(uid)
            self.set_voters(voters)

            self.current -= 1
            if self.current <= -self.target:
                self.result_reject()
            else:
                self.save()