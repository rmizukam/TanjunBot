from __future__ import annotations
import asyncio
import logging

from typing import Any, Callable
from functools import partial
from unicodedata import name

import hikari
from hikari.traits import EntityFactoryAware
from hikari import InteractionCreateEvent
from hikari.interactions.base_interactions import ResponseType
from hikari.embeds import Embed
from hikari.messages import ButtonStyle
import tanjun
from tanjun.abc import SlashContext
import random

from hikari.events.message_events import GuildMessageCreateEvent
from functions import embedStratChoice, unload_csv

valMap = None
mapList = ['Bind', 'Ascent', 'Icebox', 'Fracture', 'Split', 'Breeze', 'Haven']

agentsArray = unload_csv('./dataFiles/agentlist.csv', 'Agent_Name')
genNameSR = unload_csv('./datafiles/GeneralStrats.csv', 'name')
genStratSR = unload_csv('./datafiles/GeneralStrats.csv', 'strat')
attackStratNameArray = unload_csv('./dataFiles/AttackStrats.csv', 'name')
defenseStratNameArray = unload_csv('./dataFiles/DefenseStrats.csv', 'name')
attackStrategiesArray = unload_csv('./datafiles/AttackStrats.csv', 'strat')
defenseStrategiesArray = unload_csv('./datafiles/DefenseStrats.csv', 'strat')
dbindStrategiesArray = unload_csv('./dataFiles/dBindStrats.csv', 'strat')
dbindNamesArray = unload_csv('./dataFiles/dBindStrats.csv', 'name')
aStratHavenNameArray = unload_csv('./dataFiles/aHavenStrats.csv', 'name')
aStratHavenStratArray = unload_csv('./dataFiles/aHavenStrats.csv', 'strat')


EMBED_MENU = {
    "⚔": {"title": "Attack", "style": ButtonStyle.SECONDARY},
    '🛡': {'title': 'Defense', 'style': ButtonStyle.SECONDARY},
    '👨‍👩‍👧‍👦': {'title': 'Comp', 'style': ButtonStyle.SECONDARY},
    "🗺": {'title': 'Choose Map', 'style': ButtonStyle.SECONDARY},
    "❌": {"title": "Exit", "style": ButtonStyle.DANGER}
}

component = tanjun.Component()

embed = component.with_slash_command(
    tanjun.slash_command_group(
                               "embed",
                               "Work with Embeds!",
                               default_to_ephemeral=False)
                                    )


@embed.with_command
@tanjun.as_slash_command("valbot", "Build an Embed!")
async def valbot(
    ctx: SlashContext,
    bot: hikari.GatewayBot = tanjun.injected(type=hikari.GatewayBot),
    client: tanjun.Client = tanjun.injected(type=tanjun.Client)
) -> None:
    building_embed = hikari.Embed(title="Choose Map")
    building_embed.add_field('Strat Roulette', value='strategy')
    await embed_builder_loop(ctx, building_embed, bot=bot, client=client)


async def embed_builder_loop(
    ctx: SlashContext,
    building_embed: hikari.Embed,
    bot: hikari.GatewayBot,
    client: tanjun.Client,
):
    menu = build_menu(ctx)
    client.metadata['embed'] = building_embed
    client.metadata["roles"] = []
    client.metadata["text"] = ""
    client.metadata["pin"] = False

    await ctx.edit_initial_response(
            "Choose an option below. When finished press \"Cancel\"",
            embed=client.metadata['embed'],
            components=[*menu]
        )
    try:
        async with bot.stream(
                    InteractionCreateEvent,
                    timeout=60).filter(
                        (
                            'interaction.user.id',
                            ctx.author.id
                         )
                    ) as stream:
            async for event in stream:
                key = event.interaction.custom_id
                selected = EMBED_MENU[key]
                if selected['title'] == "Exit":
                    global valMap
                    valMap = None

                    client.metadata['embed'].edit_field(
                            0,
                            "Valbot has emptied the coomtank",
                            'visit twitch.tv/hyoon to refill',
                            inline=False
                        )
                    await ctx.edit_initial_response(
                            content="Exiting!",
                            embed=client.metadata['embed'],
                            components=[]
                        )
                    return

                await event.interaction.create_initial_response(
                    ResponseType.DEFERRED_MESSAGE_UPDATE,
                )

                await globals()[
                            f"{selected['title'].lower().replace(' ','_')}"
                        ](ctx, bot, client)
                await ctx.edit_initial_response(
                        'Choose an option below. When finished press "Cancel"',
                        embed=client.metadata['embed'],
                        components=[*menu]
                    )
    except asyncio.TimeoutError:
        await ctx.edit_initial_response(
                "Waited for 60 seconds... Timeout.",
                embed=None,
                components=[]
            )


def build_menu(ctx: SlashContext):
    menu = list()
    menu_count = 0
    last_menu_item = list(EMBED_MENU)[-1]
    row = ctx.rest.build_action_row()
    for emote, options in EMBED_MENU.items():
        (
            row.add_button(options['style'], emote)
            .set_label(options["title"])
            .set_emoji(emote)
            .add_to_container()
        )
        menu_count += 1
        if menu_count == 5 or last_menu_item == emote:
            menu.append(row)
            row = ctx.rest.build_action_row()
            menu_count = 0

    return menu


async def choose_map(
            ctx: SlashContext,
            bot: hikari.GatewayBot,
            client: tanjun.Client
        ):
    embed_dict, *_ = bot.entity_factory.serialize_embed(
            client.metadata['embed']
        )
    await ctx.edit_initial_response(
                                    content="Type in chat to set map:",
                                    components=[]
                                    )
    event = await collect_response(ctx)
    embed_dict['title'] = event.content[:200].lower().capitalize()
    global mapList
    while embed_dict['title'] not in mapList:
        await ctx.edit_initial_response(
                                    content="Invalid Map, Try Again:",
                                    components=[]
                                    )
        event = await collect_response(ctx)
        embed_dict['title'] = event.content[:200].lower().capitalize()
    client.metadata['embed'] = bot.entity_factory.deserialize_embed(embed_dict)
    global valMap
    valMap = embed_dict['title']
    await event.message.delete()


async def defense(
            ctx: SlashContext,
            bot: hikari.GatewayBot,
            client: tanjun.Client
        ):
    embed_dict, *_ = bot.entity_factory.serialize_embed(
        client.metadata['embed']
        )
    await ctx.edit_initial_response(components=[])
    global genNameSR, genStratSR
    global valMap, defenseStratNameArray, defenseStrategiesArray
    if valMap == "Bind":
        global dbindNamesArray, dbindStrategiesArray
        dNamesArray = (
                        genNameSR +
                        defenseStratNameArray +
                        dbindNamesArray
                        )
        dStratArray = (
                        genStratSR +
                        defenseStrategiesArray +
                        dbindStrategiesArray
                        )
    elif valMap == "Ascent":
        dNamesArray = (
                        genNameSR +
                        defenseStratNameArray
                        )
        dStratArray = (
                        genStratSR +
                        defenseStrategiesArray
                        )
    elif valMap == "Haven":
        dNamesArray = (
                        genNameSR +
                        defenseStratNameArray
                        )
        dStratArray = (
                        genStratSR +
                        defenseStrategiesArray
                        )
    elif valMap == "Split":
        dNamesArray = (
                        genNameSR +
                        defenseStratNameArray
                        )
        dStratArray = (
                        genStratSR +
                        defenseStrategiesArray
                        )
    elif valMap == "Fracture":
        dNamesArray = (
                        genNameSR +
                        defenseStratNameArray
                        )
        dStratArray = (
                        genStratSR +
                        defenseStrategiesArray
                        )
    elif valMap == "Icebox":
        dNamesArray = (
                        genNameSR +
                        defenseStratNameArray
                        )
        dStratArray = (
                        genStratSR +
                        defenseStrategiesArray
                        )
    elif valMap == "Breeze":
        dNamesArray = (
                        genNameSR +
                        defenseStratNameArray
                        )
        dStratArray = (
                        genStratSR +
                        defenseStrategiesArray
                        )
    else:
        dNamesArray = (
                        genNameSR +
                        defenseStratNameArray
                        )
        dStratArray = (
                        genStratSR +
                        defenseStrategiesArray
                        )
    nameRoll, stratRoll = embedStratChoice(
            dNamesArray,
            dStratArray,
        )
    if '($randplayer)' in stratRoll:
        randPlayer = random.choice(
            ['Player 1', 'Player 2', 'Player 3', 'Player 4', 'Player 5']
        )
        stratRoll.replace('($randplayer)', randPlayer)
    client.metadata['embed'].edit_field(0, nameRoll, stratRoll, inline=False)
    await ctx.edit_initial_response(
            embed=client.metadata['embed'],
            components=[]
        )


async def attack(
            ctx: SlashContext,
            bot: hikari.GatewayBot,
            client: tanjun.Client
        ):
    embed_dict, *_ = bot.entity_factory.serialize_embed(
            client.metadata['embed']
        )
    await ctx.edit_initial_response(components=[])
    global genNameSR, genStratSR
    global valMap, attackStratNameArray, attackStrategiesArray
    if valMap == "Bind":
        aNamesArray = (
                        genNameSR +
                        attackStratNameArray
                        )
        aStratArray = (
                        genStratSR +
                        attackStrategiesArray
                        )
    elif valMap == "Ascent":
        aNamesArray = (
                        genNameSR +
                        attackStratNameArray
                        )
        aStratArray = (
                        genStratSR +
                        attackStrategiesArray
                        )
    elif valMap == "Haven":
        global aStratHavenNameArray, aStratHavenStratArray
        aNamesArray = (
                        genNameSR +
                        attackStratNameArray +
                        aStratHavenNameArray
                        )
        aStratArray = (
                        genStratSR +
                        attackStrategiesArray +
                        aStratHavenStratArray
                        )
    elif valMap == "Split":
        aNamesArray = (
                        genNameSR +
                        attackStratNameArray
                        )
        aStratArray = (
                        genStratSR +
                        attackStrategiesArray
                        )
    elif valMap == "Fracture":
        aNamesArray = (
                        genNameSR +
                        attackStratNameArray
                        )
        aStratArray = (
                        genStratSR +
                        attackStrategiesArray
                        )
    elif valMap == "Icebox":
        aNamesArray = (
                        genNameSR +
                        attackStratNameArray
                        )
        aStratArray = (
                        genStratSR +
                        attackStrategiesArray
                        )
    elif valMap == "Breeze":
        aNamesArray = (
                        genNameSR +
                        attackStratNameArray
                        )
        aStratArray = (
                        genStratSR +
                        attackStrategiesArray
                        )
    else:
        aNamesArray = (
                        genNameSR +
                        attackStratNameArray
                        )
        aStratArray = (
                        genStratSR +
                        attackStrategiesArray
                        )
    nameRoll, stratRoll = embedStratChoice(
            aNamesArray,
            aStratArray,
        )
    if '($randplayer)' in stratRoll:
        randPlayer = random.choice(
            ['Player 1', 'Player 2', 'Player 3', 'Player 4', 'Player 5']
        )
        stratRoll = stratRoll.replace('($randplayer)', randPlayer)
    client.metadata['embed'].edit_field(0, nameRoll, stratRoll, inline=False)
    await ctx.edit_initial_response(
            embed=client.metadata['embed'],
            components=[]
        )


async def comp(
            ctx: SlashContext,
            bot: hikari.GatewayBot,
            client: tanjun.Client
        ):
    embed_dict, *_ = bot.entity_factory.serialize_embed(
            client.metadata['embed']
        )
    await ctx.edit_initial_response(components=[])
    global agentsArray
    composition = {random.choice(agentsArray)}
    while len(composition) != 5:
        composition.add(random.choice(agentsArray))
        compo = ', '.join(composition)
    client.metadata['embed'].edit_field(0, 'Composition', compo, inline=False)
    await ctx.edit_initial_response(
            embed=client.metadata['embed'],
            components=[]
        )


async def collect_response(
            ctx: SlashContext,
            validator: list[str] | Callable | None = None,
            timeout: int = 60,
            timeout_msg: str = "Waited for 60 seconds... Timeout."
        ) -> GuildMessageCreateEvent | None:
    def is_author(event: GuildMessageCreateEvent):
        if ctx.author == event.message.author:
            return True
        return False
    while True:
        try:
            event = await ctx.client.events.wait_for(
                        GuildMessageCreateEvent,
                        predicate=is_author,
                        timeout=timeout
                    )
        except asyncio.TimeoutError:
            await ctx.edit_initial_response(timeout_msg)
            return None

        if event.content == "❌":
            return None

        if not validator:
            return event

        elif isinstance(validator, list):
            if any(valid_resp.lower() == event.content.lower()
                    for valid_resp in validator):
                return event
            else:
                validation_message = await ctx.respond(
                        f'''That wasn't a valid response... Expected one these:
                            {' - '.join(validator)}'''
                    )
                await asyncio.sleep(3)
                await validation_message.delete()

        elif asyncio.iscoroutinefunction(validator):
            valid = await validator(ctx, event)
            if valid:
                return event
            else:
                validation_message = await ctx.respond(
                    "That doesn't look like a valid response... Try again?"
                    )
                await asyncio.sleep(3)
                await validation_message.delete()

        elif isinstance(validator, Callable):
            if validator(ctx, event):
                return event
            else:
                validation_message = await ctx.respond(
                    f"Something about that doesn't look right... Try again?"
                    )
                await asyncio.sleep(3)
                await validation_message.delete()


def is_int(ctx, event):
    try:
        int(event.content)
        return event
    except ValueError:
        pass


@ tanjun.as_loader
def load(client: tanjun.abc.Client) -> None:
    client.add_component(component.copy())
