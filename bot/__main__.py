import sys
sys.path.append(".")

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','py_elemental.settings')

from threading import Thread
import socket
import django
import asyncio
django.setup()

from element.models import Element, Recipe, Suggestion
from .models import DiscordUser, DiscordChannel
from asgiref.sync import sync_to_async
import struct
import discord

print("Django was loaded")

import os
import random
#from dotenv import load_dotenv

from discord.ext import commands

#load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

PREFIX = '-'
VOTE_TEXT ="""
:arrow_up:     {up_count}
:arrow_down:    {down_count}
"""
# 2
bot = commands.Bot(command_prefix=PREFIX)

def individual_connection_thread(conn, addr):
    length = conn.recv(8)
    bot.loop.create_task(on_socket_message(conn.recv(struct.unpack('<Q', length)[0])))
    


HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

def socket_thread():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        s.bind((HOST, PORT))
        s.listen()
        while True:
            print("accepting")
            conn, addr = s.accept()
            print("accepted")
            Thread(target=individual_connection_thread, args=(conn, addr)).start()


def send_to_all(data: bytes):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(struct.pack('<Q', len(data)) + data)


Thread(target=socket_thread).start()

def sentencify(l, ender = ", ", format = "`{}`", separator = ", "):
    s = ""
    for idx, i in enumerate(l):
        if not idx:
            s += format.format(i)
        elif idx == len(l) - 1:
            s += ender + format.format(i)
        else:
            s += separator + format.format(i)

    return s

defaults = list(Element.objects.filter(default=True).all())

def validate_user(user: DiscordUser):
    lacks = set(defaults) - set(user.has_elements.all())
    for i in lacks:
        user.has_elements.add(i)

    user.save()

def sync_response_to(message, contents):
    bot.loop.create_task(message.channel.send(message.author.mention + " " + contents))

def handle_ingredients(message, ingredient_names):
    print("ingredients")
    ingredients = [Element.objects.filter(name__iexact=i).first() for i in ingredient_names]

    unknown = []
    for k, v in zip(ingredient_names, ingredients):
        if v is None:
            unknown.append(k)

    error_response = ""
    if unknown:
        error_response += f"The following elements were not found: {sentencify(unknown, ' and ')}\n"
        

    author = get_or_create(DiscordUser, message.author.id)

    validate_user(author)
    
    lacks = set(ingredients) - set(author.has_elements.all())
    lacks = list(filter(lambda i: i, lacks))
    if lacks:
        error_response += f"You don't have the following elements: {sentencify([i.name for i in lacks], ' and ')}\n"
        
    if bool(lacks) or bool(unknown):
        print("Error ")
        sync_response_to(message, error_response)
        return

    author.last_ingredients = ','.join(str(i.sequential_number) for i in ingredients)
    author.save()

    recipes = list(Recipe.result_of(ingredients))
    
    if len(recipes) == 0:
        sync_response_to(message, f"That combination doesn't exist, but you can create it with {PREFIX}suggest <new element name>")
        return

    else:
        if recipes[0].result in author.has_elements.all():
            sync_response_to(message, 
                f":new: You made {recipes[0].result.discord_name}, but already have it"
                )
        else:
            author.has_elements.add(recipes[0].result)
            author.save()
            sync_response_to(message, 
                f":new: You unlocked a new element: {recipes[0].result.discord_name}"
                )


def handle_play_message(message):
    ingredients = []
    if "\n" in message.content:
        for i in message.content.split('\n'):
            ingredients.append(i.strip())
        handle_ingredients(message, ingredients)
    elif "+" in message.content:
        for i in message.content.split('+'):
            ingredients.append(i.strip())
        handle_ingredients(message, ingredients)

@sync_to_async
def sync_on_message(message):
    if message.content.startswith(PREFIX):
        return # Handled by command

    channel = DiscordChannel.objects.filter(id=message.channel.id).first()


    if not channel:
        print("Channel not configured")
        return # Channel not configured for anything

    if channel.play_channel:
        handle_play_message(message)

def send_suggestion(suggestion: Suggestion):
    embed = discord.Embed(
        title=f"Voting: {suggestion.result.discord_name}",
        description=f"{sentencify([i.discord_name for i in suggestion.ingredients], '+', separator = '+')} = {result.discord_name} "  + VOTE_TEXT.format(
            up_count=0,
            down_count=0
        ) ,
    )
    embed.set_footer(
        text=f"\nSuggested by 3\nSuggested in 3\n"
    )

    #voting["footer"] = f"\nSuggested by {message.author}\nSuggested in {message.guild.name}\n"
    
    for channel in DiscordChannel.objects.filter(vote_channel=True).all():
        channel = bot.get_channel(channel.id)

        bot.loop.create_task(channel.send())


@sync_to_async
def sync_suggest(message, element_name):

    author = get_or_create(DiscordUser, message.author.id)

    validate_user(author)

    if not author.last_ingredients:
        sync_response_to(message, f"You need to try out a combination first!")
    else:
        sync_response_to(message, f"Suggested {sentencify([Element.objects.filter(sequential_number=i).first().name for i in author.last_ingredients.split(',')], '+', separator='+')} = `{element_name}`")
        s = Suggestion(ingredients=author.last_ingredients, name=element_name)
        s.save()
        send_suggestion(s)

@bot.command()
async def suggest(ctx, new_name: str):
    await sync_suggest(ctx.message, new_name)

async def on_socket_message(message):
    if message == "new suggestion update":
        pass

@bot.listen()
async def on_message(message):
    if message.author == bot.user:
        return

    await sync_on_message(message)

CHANNEL_SETTINGS = ['vote', 'play']

def get_or_create(cls, id):
    obj = cls.objects.filter(id=id).first()
    if not obj:
        return cls.objects.create(id=id)

    print("obj", id)

    return obj

@sync_to_async
def sync_enable_channel_for(id: int, setting: str):
    obj = get_or_create(DiscordChannel, id)
    setattr(obj, setting + "_channel", True)
    print("end")
    obj.save()

@sync_to_async
def sync_disable_channel_for(id: int, setting: str):
    obj = get_or_create(DiscordChannel, id)
    setattr(obj, setting + "_channel", False)
    obj.save()

@bot.command()
async def enable_channel_for(ctx, setting_name: str):
    if setting_name not in CHANNEL_SETTINGS:
        _vals = [f"'{i}'" for i in CHANNEL_SETTINGS]
        await ctx.send(f"Invalid channel setting! (choose between {sentencify(CHANNEL_SETTINGS, ' or ')})")
        return

    await sync_enable_channel_for(ctx.message.channel.id, setting_name)


@bot.command()
async def disable_channel_for(ctx, setting_name: str):
    if setting_name not in CHANNEL_SETTINGS:
        await ctx.send(f"Invalid channel setting! (choose between {sentencify(CHANNEL_SETTINGS, ' or ')})")
        return

    await sync_disable_channel_for(ctx.message.channel.id, setting_name)


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

bot.run(TOKEN)
