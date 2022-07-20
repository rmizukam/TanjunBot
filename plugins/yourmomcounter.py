import collections
import hikari
import typing
import tanjun
import random
import csv
import re
from functions import psudoRanChoice, unload_csv, incrTxt

component = tanjun.Component()

urmomma = unload_csv('./dataFiles/waystosayurmom.csv', 'way')


@component.with_listener(hikari.MessageCreateEvent)
async def on_message(event: hikari.MessageCreateEvent):
    pathmomtxt = './dataFiles/urmomcounter.txt'
    if event.is_human:
        mc = event.content
        if type(mc) == str:
            mc = mc.lower()
            urMomFound = re.search(r"\bur mom\b", mc)
                #r"" needed since \ is used
            yourMomFound = re.search(r'\byour mom\b', mc)
            yoMomFound = re.search(r"\byo mom\b", mc)
            if urMomFound or yourMomFound or yoMomFound:
                with open(pathmomtxt, 'r') as f:
                    count = str(int(f.read()) + 1)
                with open(pathmomtxt, 'w') as f:
                    f.write(count)
                await event.message.respond(
                    '\"Your mom\" has been said ' + count + ' times.'
                )

@tanjun.as_loader
def load_module(client: tanjun.abc.Client) -> None:
    client.add_component(component.copy())


@tanjun.as_unloader
def unload_component(client: tanjun.abc.Client) -> None:
    client.remove_component_by_name(component.name)
