import collections
import hikari
import typing
import tanjun
import random
import os
from functions import psudoRanChoice, unload_csv
from dotenv import load_dotenv
load_dotenv()


component = tanjun.Component()

NSFWChannels = [int(os.getenv('SUMMONCHANNELKEY')),
                int(os.getenv('BOTTESTERCHANNELID')),
                int(os.getenv('HENTISENTIKEY'))
                ]

wayHyoon = ['hyn', 'hyba']
henti = unload_csv('./dataFiles/h.csv', 'content')
hyooba = unload_csv('./dataFiles/Hyooba.csv', 'content')
# ahra = unload_csv('./dataFiles/Ahra.csv', 'content')
# jinny = unload_csv('./dataFiles/Jinny.csv', 'content')
# poki = unload_csv('./dataFiles/pokilinks.csv', 'content')
# tenga = unload_csv('./dataFiles/tenga.csv', 'content')

thenti = set()
thyooba = set()
# tahra = set()
# tjinny = set()
# tpoki = set()
# ttenga = set()


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
            msg = msg.replace('o', '')
            if any(phrase in msg for phrase in wayHyoon):
                x = random.randint(2, 100)
                string = 'Hy'
                for i in range(1, x+1):
                    string = string + 'o'
                string = string + random.choice(['n', 'ba'])
                global thyooba
                img, thyooba = psudoRanChoice(hyooba, thyooba)
                if event.channel_id in NSFWChannels:
                    await event.message.respond(string)
                    await event.message.respond(img)
                else:
                    await event.message.respond(string)


@tanjun.as_loader
def load_module(client: tanjun.abc.Client) -> None:
    client.add_component(component.copy())


@tanjun.as_unloader
def unload_component(client: tanjun.abc.Client) -> None:
    client.remove_component_by_name(component.name)
