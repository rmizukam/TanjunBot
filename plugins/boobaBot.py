from __future__ import annotations
import asyncio
import logging

from typing import Any, Callable
from functools import partial

import hikari
from hikari.traits import EntityFactoryAware
from hikari import InteractionCreateEvent
from hikari.interactions.base_interactions import ResponseType
from hikari.embeds import Embed
from hikari.messages import ButtonStyle
import tanjun
import random
from tanjun.abc import SlashContext
from functions import psudoRanChoice, unload_csv
from hikari.events.message_events import GuildMessageCreateEvent

nl = "\n"
thyooba = set()
hyoobaArray = unload_csv('./dataFiles/Hyooba.csv', 'content')


EMBED_MENU = {
    "📋": {"title": "Hyooba", "style": ButtonStyle.SECONDARY},
}
EMBED_OK = {
    "❌": {"title": "Cancel", "style": ButtonStyle.DANGER}
}

EMBED_MENU_FULL = EMBED_MENU | EMBED_OK

component = tanjun.Component()

henti = component.with_slash_command(
    tanjun.slash_command_group("henti",
                               "Work with Embeds! (Requires Can Embed)",
                               default_to_ephemeral=False)
    )


# @henti.with_command
# @tanjun.with_str_slash_option("message_id", "The Message Id to edit.")
# @tanjun.as_slash_command("interactive-edit", f"Edit an Embed!")
# async def interactive_edit(
#     ctx: SlashContext,
#     message_id: hikari.Message,
#     bot: hikari.GatewayBot = tanjun.injected(type=hikari.GatewayBot),
#     client: tanjun.Client = tanjun.injected(type=tanjun.Client)
# ):
#     message = None
#     guild = ctx.get_guild()
#     if not guild:
#         return
#     channels = guild.get_channels()

#     for channel_id in channels:
#         channel = guild.get_channel(channel_id)
#         if not channel:
#             continue
#         if hasattr(channel, "fetch_message"):
#             try:
#                 message = await channel.fetch_message(message_id)
#                 if message:
#                     break
#             except hikari.NotFoundError:
#                 pass
#     if not message:
#         await ctx.respond("I couldn't find that message...")
#         return
#     await embed_builder_loop(ctx, message.embeds[0], bot=bot, client=client)


@henti.with_command
@tanjun.as_slash_command("boobabot", "booba!")
async def booba_bot(
    ctx: SlashContext,
    bot: hikari.GatewayBot = tanjun.injected(type=hikari.GatewayBot),
    client: tanjun.Client = tanjun.injected(type=tanjun.Client)
) -> None:
    building_embed = Embed(title="boobabot ready to coom")

    await embed_builder_loop(ctx, building_embed, bot=bot, client=client)


async def embed_builder_loop(
    ctx: SlashContext,
    building_embed: Embed,
    bot: hikari.GatewayBot,
    client: tanjun.Client,
):
    menu = build_menu(ctx)
    client.metadata['embed'] = building_embed
    client.metadata["roles"] = []
    client.metadata["text"] = ""
    client.metadata["pin"] = False

    await ctx.edit_initial_response(
        "boobalicious",
        embed=client.metadata['embed'], components=[*menu]
        )
    try:
        async with bot.stream(
                    InteractionCreateEvent,
                    timeout=300
                ).filter(
                         ('interaction.user.id',
                          ctx.author.id
                          )
                         ) as stream:
            async for event in stream:
                key = event.interaction.custom_id
                selected = EMBED_MENU_FULL[key]
                if selected['title'] == "Cancel":
                    await ctx.edit_initial_response(
                                                    content=f"Exiting!",
                                                    components=[]
                                                    )
                    return

                await event.interaction.create_initial_response(
                    ResponseType.DEFERRED_MESSAGE_UPDATE,
                )

                await globals()[
                    f'''{selected['title'].lower().replace(' ', '_')}'''
                    ](ctx, bot, client)
                await ctx.edit_initial_response(
                    '''Click/Tap your choice below,
                       then watch the embed update!''',
                    embed=client.metadata['embed'],
                    components=[*menu]
                    )
    except asyncio.TimeoutError:
        await ctx.edit_initial_response(
            "Waited for 5 minutes... Timeout.",
            embed=None, components=[]
            )


def build_menu(ctx: SlashContext) -> list[Any]:
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

    confirmation_row = ctx.rest.build_action_row()
    for emote, options in EMBED_OK.items():
        (
            confirmation_row.add_button(options['style'], emote)
            .set_label(options["title"])
            .set_emoji(emote)
            .add_to_container()
        )
    menu.append(confirmation_row)

    return menu
# -----------------------------------------------------------------------------------------------------


async def hyooba(
            ctx: SlashContext,
            bot: hikari.GatewayBot,
            client: tanjun.Client
        ):
    global thyooba
    embed_dict, *_ = bot.entity_factory.serialize_embed(
            client.metadata['embed']
        )
    x = random.randint(2, 100)
    string = 'Hy'
    for i in range(1, x+1):
        string = string + 'o'
    string = string + random.choice(['n', 'ba'])
    embed_dict['title'] = string
    img, thyooba = psudoRanChoice(hyoobaArray, thyooba)
    client.metadata['embed'].set_image(img)
    await ctx.edit_initial_response(
            embed=client.metadata['embed'],
            components=[]
        )


async def collect_response(
        ctx: SlashContext,
        validator: list[str] | Callable | None = None,
        timeout: int = 300,
        timeout_msg: str = '''Waited for 5 minutes...
                               Timeout.''') -> GuildMessageCreateEvent | None:
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
            if (any(valid_resp.lower() == event.content.lower()
                    for valid_resp in validator)):
                return event
            else:
                validation_message = await ctx.respond(
                        f'''That wasn't a valid response...
                             Expected one these: {' - '.join(validator)}'''
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


async def ensure_guild_channel(ctx, event):
    guild = ctx.get_guild()
    channels = guild.get_channels()
    found_channel = None

    for channel_id in channels:
        channel = guild.get_channel(channel_id)
        if str(channel.id) in event.content or channel.name == event.content:
            found_channel = channel
            break

    if found_channel:
        return True

    await ctx.edit_initial_response(
            content=f"Channel `{event.content}` not found! Try again?"
        )
    await event.message.delete()
    await asyncio.sleep(5)


@ tanjun.as_loader
def load(client: tanjun.abc.Client) -> None:
    client.add_component(component.copy())
