import collections
import hikari
import typing
import tanjun
import random
import csv
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
            if mc in urmomma:
                with open(pathmomtxt, 'r') as f:
                    count = str(int(f.read()) + 1)
                with open(pathmomtxt, 'w') as f:
                    f.write(count)
                await event.message.respond(
                    '\"Your mom\" has been said ' + count + ' times.'
                )
            elif mc.endswith('your mom') or mc.endswith(' ur mom'):
                with open(pathmomtxt, 'r') as f:
                    count = str(int(f.read()) + 1)
                with open(pathmomtxt, 'w') as f:
                    f.write(count)
                await event.message.respond(
                    '\"Your mom\" has been said ' + count + ' times.'
                )
            elif (mc.find('ur mom') != -1 and
                  mc.endswith('your mom') is not True and
                  mc.endswith(' ur mom') is not True
                  ):
                charA = mc[mc.find('mom') + 3]
                charB4Y = mc[mc.find('mom') - 6]
                charB4u = mc[mc.find('mom') - 4]
                if charA == "'" or charA == 's' or charA.isspace():
                    if charB4Y.isspace() or charB4u.isspace():
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
