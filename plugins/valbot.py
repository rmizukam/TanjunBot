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

from hikari.events.message_events import GuildMessageCreateEvent
from functions import embedStratChoice, unload_csv

acount = set()
dcount = set()

agentsArray = unload_csv('./dataFiles/agentlist.csv', 'Agent_Name')
generalStratNameArray = unload_csv('./datafiles/GeneralStrats.csv', 'name')
attackStratNameArray = unload_csv('./dataFiles/AttackStrats.csv', 'name')
defenseStratNameArray = unload_csv('./dataFiles/DefenseStrats.csv', 'name')
generalStrategiesArray = unload_csv('./datafiles/GeneralStrats.csv', 'strat')
attackStrategiesArray = unload_csv('./datafiles/AttackStrats.csv', 'strat')
defenseStrategiesArray = unload_csv('./datafiles/DefenseStrats.csv', 'strat')

aNamesArray = generalStratNameArray + attackStratNameArray
aStratArray = generalStrategiesArray + attackStrategiesArray
dNamesArray = generalStratNameArray + defenseStratNameArray
dStratArray = generalStrategiesArray + defenseStrategiesArray



EMBED_MENU = {
    "⚔": {"title": "Attack", "style": ButtonStyle.SECONDARY},
    '🛡': {'title': 'Defense', 'style': ButtonStyle.SECONDARY},
    "🗺": {'title': 'Choose Map', 'style': ButtonStyle.SECONDARY},
    "❌": {"title": "Cancel", "style": ButtonStyle.DANGER}
}

component = tanjun.Component()

embed = component.with_slash_command(tanjun.slash_command_group("embed", "Work with Embeds!", default_to_ephemeral=False))


@embed.with_command
@tanjun.as_slash_command("valbot", f"Build an Embed!")
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

    await ctx.edit_initial_response("Click/Tap your choice below.", embed=client.metadata['embed'], components=[*menu])
    try:
        async with bot.stream(InteractionCreateEvent, timeout=60).filter(('interaction.user.id', ctx.author.id)) as stream:
            async for event in stream:
                key = event.interaction.custom_id
                selected = EMBED_MENU[key]
                if selected['title'] == "Cancel":
                    await ctx.edit_initial_response(content=f"Exiting!", components=[])
                    return

                await event.interaction.create_initial_response(
                    ResponseType.DEFERRED_MESSAGE_UPDATE,
                )

                await globals()[f"{selected['title'].lower().replace(' ', '_')}"](ctx, bot, client)
                await ctx.edit_initial_response("Click/Tap your choice below, then watch the embed update!", embed=client.metadata['embed'], components=[*menu])
    except asyncio.TimeoutError:
        await ctx.edit_initial_response("Waited for 60 seconds... Timeout.", embed=None, components=[])


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


async def choose_map(ctx: SlashContext, bot: hikari.GatewayBot, client: tanjun.Client):
    embed_dict, *_ = bot.entity_factory.serialize_embed(client.metadata['embed'])
    await ctx.edit_initial_response(content="Set Map:", components=[])
    event = await collect_response(ctx)
    embed_dict['title'] = event.content[:200]
    client.metadata['embed'] = bot.entity_factory.deserialize_embed(embed_dict)
    # print(embed_dict['title'])
    print(embed_dict)
    await event.message.delete()


async def defense(ctx: SlashContext, bot: hikari.GatewayBot, client: tanjun.Client):
    embed_dict, *_ = bot.entity_factory.serialize_embed(client.metadata['embed'])
    await ctx.edit_initial_response(content="You Chose Defense:", components=[])
    global dcount, dNamesArray, dStratArray
    nameRoll, stratRoll, dcount = embedStratChoice(dNamesArray, dStratArray, dcount)
    client.metadata['embed'].edit_field(0, nameRoll, stratRoll, inline=False)
    await ctx.edit_initial_response(content="Good Luck!", embed=client.metadata['embed'], components=[])


async def attack(ctx: SlashContext, bot: hikari.GatewayBot, client: tanjun.Client):
    embed_dict, *_ = bot.entity_factory.serialize_embed(client.metadata['embed'])
    await ctx.edit_initial_response(content="You Chose Attack:", components=[])
    global acount, aNamesArray, aStratArray
    nameRoll, stratRoll, acount = embedStratChoice(aNamesArray, aStratArray, acount)
    client.metadata['embed'].edit_field(0, nameRoll, stratRoll, inline=False)
    await ctx.edit_initial_response(content="Good Luck!", embed=client.metadata['embed'], components=[])


async def collect_response(ctx: SlashContext, validator: list[str] | Callable | None = None, timeout: int = 60, timeout_msg: str = "Waited for 60 seconds... Timeout.") -> GuildMessageCreateEvent | None:
    def is_author(event: GuildMessageCreateEvent):
        if ctx.author == event.message.author:
            return True
        return False
    while True:
        try:
            event = await ctx.client.events.wait_for(GuildMessageCreateEvent, predicate=is_author, timeout=timeout)
        except asyncio.TimeoutError:
            await ctx.edit_initial_response(timeout_msg)
            return None

        if event.content == "❌":
            return None

        if not validator:
            return event

        elif isinstance(validator, list):
            if any(valid_resp.lower() == event.content.lower() for valid_resp in validator):
                return event
            else:
                validation_message = await ctx.respond(f"That wasn't a valid response... Expected one these: {' - '.join(validator)}")
                await asyncio.sleep(3)
                await validation_message.delete()

        elif asyncio.iscoroutinefunction(validator):
            valid = await validator(ctx, event)
            if valid:
                return event
            else:
                validation_message = await ctx.respond("That doesn't look like a valid response... Try again?")
                await asyncio.sleep(3)
                await validation_message.delete()

        elif isinstance(validator, Callable):
            if validator(ctx, event):
                return event
            else:
                validation_message = await ctx.respond(f"Something about that doesn't look right... Try again?")
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
