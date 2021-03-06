import collections
import hikari
import typing
import tanjun
import random
import os
from functions import psudoRanChoice, unload_csv
from dotenv import load_dotenv
import re

load_dotenv()


component = tanjun.Component()

NSFWChannels = [int(os.getenv('SUMMONCHANNELKEY')),
                int(os.getenv('BOTTESTERCHANNELID')),
                int(os.getenv('HENTISENTIKEY'))
                ]

wayHyoon = ['hyn', 'hyba']
henti = unload_csv('./dataFiles/h.csv', 'content')
hyooba = unload_csv('./dataFiles/Hyooba.csv', 'content')
hyoofa = unload_csv('./dataFiles/Hyoofa.csv', 'content')

thenti = set()
thyooba = set()
thyoofa = set()


@component.with_listener(hikari.MessageCreateEvent)
async def on_message_create(event: hikari.MessageCreateEvent):
    global NSFWChannels, thyooba, thenti
    if event.is_human:
        msg = event.content
        if type(msg) == str:
            msg = msg.lower()
            if 'hentai' in msg:
                img, thenti = psudoRanChoice(henti, thenti)
                if event.channel_id in NSFWChannels:
                    await event.message.respond(img)
            hyoonFound = re.search(r"\bhyoo+n\b", msg)
            hyoobaFound = re.search(r"\bhyoo+ba\b", msg)
            tifaHyoonFound = re.search(r"\bti+fa\b", msg)
            if hyoonFound or hyoobaFound:
                x = random.randint(2, 100)
                string = 'Hy'
                for i in range(1, x+1):
                    string = string + 'o'
                if hyoonFound:
                    string = string + 'n'
                else:
                    string = string + 'ba'
                global thyooba
                img, thyooba = psudoRanChoice(hyooba, thyooba)
                await event.message.respond(string)
                await event.message.respond(img)
            elif tifaHyoonFound:
                x = random.randint(2, 100)
                string = 'Hy'
                for i in range(1, x+1):
                    string = string + 'o'
                string = string + 'fa'
                global thyoofa
                img, thyoofa = psudoRanChoice(hyoofa, thyoofa)
                await event.message.respond(string)
                await event.message.respond(img)


@component.with_slash_command
@tanjun.as_slash_command(
                         'hyoomer-1',
                         'Legendary Red Hyooba',
                         default_to_ephemeral=False
                        )
async def hyoomer_1(ctx: tanjun.abc.SlashContext) -> None:
    with open('./dataFiles/redHyoomer.png', 'rb') as fh:
        f = hikari.File('./dataFiles/redHyoomer.png')
    await ctx.respond('You Coomer')
    await ctx.respond(f)

@component.with_slash_command
@tanjun.as_slash_command(
                         'hyoomer-2',
                         'Wild White Hyooba'
                        )
async def hyoomer_2(ctx: tanjun.abc.SlashContext) -> None:
    with open('./dataFiles/whiteHyoomer.png', 'rb') as fh:
        f = hikari.File('./dataFiles/whiteHyoomer.png')
    await ctx.respond('COOMER')
    await ctx.respond(f)


@tanjun.as_loader
def load_module(client: tanjun.abc.Client) -> None:
    client.add_component(component.copy())


@tanjun.as_unloader
def unload_component(client: tanjun.abc.Client) -> None:
    client.remove_component_by_name(component.name)
