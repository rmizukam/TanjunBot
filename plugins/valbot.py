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
from tanjun.abc import SlashContext

from hikari.events.message_events import GuildMessageCreateEvent

nl = "\n"


EMBED_MENU = {
    "📋": {"title": "Title", "style": ButtonStyle.SECONDARY},
    "💬": {"title": "Description", "style": ButtonStyle.SECONDARY},
    "🖼️": {"title": "Change Icon", "style": ButtonStyle.SECONDARY},
    "📦": {"title": "Add Server Logo", "style": ButtonStyle.SECONDARY},
    "🎨": {"title": "Image", "style": ButtonStyle.SECONDARY},
    "👣": {"title": "Footer", "style": ButtonStyle.SECONDARY},
    "➕": {"title": "Add Field", "style": ButtonStyle.SECONDARY},
    "🖊️": {"title": "Change Field", "style": ButtonStyle.SECONDARY},
    "💢": {"title": "Remove Field", "style": ButtonStyle.SECONDARY},
    "🌈": {"title": "Color", "style": ButtonStyle.SECONDARY},
    "📰": {"title": "Change text on Publish", "style": ButtonStyle.SECONDARY},
    "📌": {"title": "Pin Embed", "style": ButtonStyle.SECONDARY},
    "🏓": {"title": "Add Ping", "style": ButtonStyle.SECONDARY},
    "❓": {"title": "Show Status", "style": ButtonStyle.SECONDARY},
}
EMBED_OK = {
    "🆗": {"title": "Publish to Channel", "style": ButtonStyle.PRIMARY},
    "❌": {"title": "Cancel", "style": ButtonStyle.DANGER}
}

EMBED_MENU_FULL = EMBED_MENU | EMBED_OK

component = tanjun.Component()

embed = component.with_slash_command(tanjun.slash_command_group("embed", "Work with Embeds! (Requires Can Embed)", default_to_ephemeral=False))


@embed.with_command
@tanjun.with_str_slash_option("message_id", "The Message Id to edit.")
@tanjun.as_slash_command("interactive-edit", f"Edit an Embed!")
async def interactive_edit(
    ctx: SlashContext,
    message_id: hikari.Message,
    bot: hikari.GatewayBot = tanjun.injected(type=hikari.GatewayBot),
    client: tanjun.Client = tanjun.injected(type=tanjun.Client)
):
    message = None
    guild = ctx.get_guild()
    if not guild:
        return
    channels = guild.get_channels()

    for channel_id in channels:
        channel = guild.get_channel(channel_id)
        if not channel:
            continue
        if hasattr(channel, "fetch_message"):
            try:
                message = await channel.fetch_message(message_id)
                if message:
                    break
            except hikari.NotFoundError:
                pass
    if not message:
        await ctx.respond("I couldn't find that message...")
        return
    await embed_builder_loop(ctx, message.embeds[0], bot=bot, client=client)


@embed.with_command
@tanjun.as_slash_command("interactive-post", f"Build an Embed!")
async def interactive_post(
    ctx: SlashContext,
    bot: hikari.GatewayBot = tanjun.injected(type=hikari.GatewayBot),
    client: tanjun.Client = tanjun.injected(type=tanjun.Client)
) -> None:
    building_embed = Embed(title="New Embed")

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

    await ctx.edit_initial_response("Click/Tap your choice below, then watch the embed update!", embed=client.metadata['embed'], components=[*menu])
    try:
        async with bot.stream(InteractionCreateEvent, timeout=60).filter(('interaction.user.id', ctx.author.id)) as stream:
            async for event in stream:
                key = event.interaction.custom_id
                selected = EMBED_MENU_FULL[key]
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


async def title(ctx: SlashContext, bot: hikari.GatewayBot, client: tanjun.Client):
    embed_dict, *_ = bot.entity_factory.serialize_embed(client.metadata['embed'])
    await ctx.edit_initial_response(content="Set Title for embed:", components=[])
    event = await collect_response(ctx)
    embed_dict['title'] = event.content[:200]
    client.metadata['embed'] = bot.entity_factory.deserialize_embed(embed_dict)
    await ctx.edit_initial_response(content="Title updated!", embed=client.metadata['embed'], components=[])
    await event.message.delete()


async def description(ctx: SlashContext, bot: hikari.GatewayBot, client: tanjun.Client):
    embed_dict, *_ = bot.entity_factory.serialize_embed(client.metadata['embed'])
    await ctx.edit_initial_response(content="Set Description for embed:", components=[])
    event = await collect_response(ctx, validator=lambda _, event: len(event.message.content) < 4096)
    embed_dict['description'] = event.content[:4090]
    client.metadata['embed'] = bot.entity_factory.deserialize_embed(embed_dict)
    await ctx.edit_initial_response(content="Description Updated!", embed=client.metadata['embed'], components=[])
    await event.message.delete()


async def change_icon(ctx: SlashContext, bot: hikari.GatewayBot, client: tanjun.Client):
    await ctx.edit_initial_response(content="Set Icon for embed:", components=[])
    event = await collect_response(ctx, validator=lambda _, event: event.message.content.startswith("http"))
    client.metadata['embed'].set_thumbnail(event.content)
    await ctx.edit_initial_response(content="Thumbnail Updated!", embed=client.metadata['embed'], components=[])
    await event.message.delete()


async def add_server_logo(ctx: SlashContext, bot: hikari.GatewayBot, client: tanjun.Client):
    client.metadata['embed'].set_thumbnail((await ctx.fetch_guild()).icon_url)
    await ctx.edit_initial_response(content="Logo Updated!", embed=client.metadata['embed'], components=[])


async def image(ctx: SlashContext, bot: hikari.GatewayBot, client: tanjun.Client):
    await ctx.edit_initial_response(content="Set Image for embed:", components=[])
    event = await collect_response(ctx, validator=lambda _, event: len(event.message.content) < 2000)
    client.metadata['embed'].set_image(event.content)
    await ctx.edit_initial_response(content="Image Updated!", embed=client.metadata['embed'], components=[])
    await event.message.delete()


async def footer(ctx: SlashContext, bot: hikari.GatewayBot, client: tanjun.Client):
    await ctx.edit_initial_response(content="Set Footer for embed:", components=[])
    event = await collect_response(ctx, validator=lambda _, event: len(event.message.content) < 2000)
    guild = await ctx.fetch_guild()
    client.metadata['embed'].set_footer(text=event.content, icon=guild.icon_url)
    await ctx.edit_initial_response(content="Footer Updated!", embed=client.metadata['embed'], components=[])
    await event.message.delete()


async def add_field(ctx: SlashContext, bot: hikari.GatewayBot, client: tanjun.Client):
    field_name = ""
    field_body = ""
    field_inline = False
    await ctx.edit_initial_response("What would you like the Field Title to be?", components=[])
    name_event = await collect_response(ctx, validator=lambda _, event: len(event.message.content) < 256)
    field_name = name_event.content
    await ctx.edit_initial_response("What would you like the Field Body to be?", components=[])
    body_event = await collect_response(ctx, validator=lambda _, event: len(event.message.content) < 4096)
    field_body = body_event.content
    await ctx.edit_initial_response("Would you like this to be inline? (y/n)", components=[])
    inline_event = await collect_response(ctx, validator=['yes', 'y', 'ye', 't', 'true', 'no', 'n', 'false', 'f'])
    if inline_event.content.lower() in ['yes', 'y', 'ye', 't', 'true']:
        field_inline = True
    elif inline_event.content.lower() in ['no', 'n', 'false', 'f']:
        field_inline = False
    else:
        await ctx.edit_initial_response("Didn't understand that answer, assuming `No`.", embed=None, components=[])
    await name_event.message.delete()
    await body_event.message.delete()
    await inline_event.message.delete()
    client.metadata['embed'].add_field(name=field_name, value=field_body, inline=field_inline)
    await ctx.edit_initial_response(content="Field Added!", embed=client.metadata['embed'], components=[])


async def change_field(ctx: SlashContext, bot: hikari.GatewayBot, client: tanjun.Client):
    fields = ""
    field_name = ""
    field_body = ""
    field_inline = False

    for k, field in enumerate(client.metadata['embed'].fields):
        k += 1
        fields += f"```{k} - {field.name}```{k}"

    await ctx.edit_initial_response(f"What Field would you like to update? Provide just the  Index Number: {nl} {fields}", components=[])
    field_idx_event = await collect_response(ctx, validator=is_int)
    field_idx = int(field_idx_event.content) - 1
    await ctx.edit_initial_response("What would you like the Field Title to be?", components=[])
    name_event = await collect_response(ctx, validator=lambda _, event: len(event.message.content) < 256)
    field_name = name_event.content
    await ctx.edit_initial_response("What would you like the Field Body to be?", components=[])
    body_event = await collect_response(ctx, validator=lambda _, event: len(event.message.content) < 4096)
    field_body = body_event.content
    await ctx.edit_initial_response("Would you like this to be inline? (y/n)", components=[])
    inline_event = await collect_response(ctx, validator=['yes', 'y', 'ye', 't', 'true', 'no', 'n', 'false', 'f'])
    if inline_event.content.lower() in ['yes', 'y', 'ye', 't', 'true']:
        field_inline = True
    elif inline_event.content.lower() in ['no', 'n', 'false', 'f']:
        field_inline = False
    else:
        await ctx.edit_initial_response("Didn't understand that answer, assuming `No`.", embed=None, components=[])
    await name_event.message.delete()
    await body_event.message.delete()
    await inline_event.message.delete()
    client.metadata['embed'].edit_field(field_idx, field_name, field_body, inline=field_inline)
    await ctx.edit_initial_response(content="Field Added!", embed=client.metadata['embed'], components=[])


async def remove_field(ctx: SlashContext, bot: hikari.GatewayBot, client: tanjun.Client):
    fields = ""
    field_name = ""
    field_body = ""
    field_inline = False

    for k, field in enumerate(client.metadata['embed'].fields):
        k += 1
        fields += f"```{k} - {field.name}```{k}"

    await ctx.edit_initial_response(f"What Field would you like to update? Provide just the  Index Number: {nl} {fields}", components=[])
    field_idx_event = await collect_response(ctx, validator=is_int)
    field_idx = int(field_idx_event.content) - 1
    client.metadata['embed'].remove_field(field_idx)
    await ctx.edit_initial_response("Removed field!", embed=client.metadata['embed'])


async def color(ctx: SlashContext, bot: hikari.GatewayBot, client: tanjun.Client):
    embed_dict, *_ = bot.entity_factory.serialize_embed(client.metadata['embed'])
    await ctx.edit_initial_response(content="Set Color for embed:", components=[])
    event = await collect_response(ctx)
    color = hikari.colors.Color(event.content)
    embed_dict['color'] = color
    client.metadata['embed'] = bot.entity_factory.deserialize_embed(embed_dict)
    await ctx.edit_initial_response(content="Color updated!", embed=client.metadata['embed'], components=[])
    await event.message.delete()


async def change_text_on_publish(ctx: SlashContext, bot: hikari.GatewayBot, client: tanjun.Client):
    await ctx.edit_initial_response(content="Set Text for Publish:", components=[])
    event = await collect_response(ctx, validator=lambda ctx, event: len(event.content) < 2000)
    client.metadata['text'] = event.content
    await ctx.edit_initial_response(content="Text for Publish updated!")
    await event.message.delete()


async def pin_embed(ctx: SlashContext, bot: hikari.GatewayBot, client: tanjun.Client):
    client.metadata['pin'] = True
    await ctx.edit_initial_response(content="Set to Pin!", components=[])
    await asyncio.sleep(3)


async def add_ping(ctx: SlashContext, bot: hikari.GatewayBot, client: tanjun.Client):
    while True:
        await ctx.edit_initial_response(content="Add Ping for Publish. To return to menu, send ❌.", components=[])
        try:
            async with bot.stream(GuildMessageCreateEvent, timeout=60).filter(('author.id', ctx.author.id)) as stream:
                async for event in stream:
                    if event.content == "❌":
                        await event.message.delete()
                        return

                    roles = await ctx.get_guild().fetch_roles()
                    found_role = None

                    for role in roles:
                        if role.id == event.content or role.name == event.content:
                            found_role = role
                            break

                    if not found_role:
                        await ctx.edit_initial_response(content=f"Role `{event.content}` not found! Try again?")
                    else:
                        client.metadata['roles'].append(role)
                        await ctx.edit_initial_response(content=f"Added {found_role.mention} to ping list for Publish!")

                    await event.message.delete()
                    await asyncio.sleep(5)
                    await ctx.edit_initial_response(content="Add Ping for Publish. To return to menu, send ❌.", components=[])
        except asyncio.TimeoutError:
            await ctx.edit_initial_response(content="Waited for 60 seconds... Timed out.")
            return None


async def show_status(ctx: SlashContext, bot: hikari.GatewayBot, client: tanjun.Client):
    roles = ""
    for role in client.metadata['roles']:
        roles += f"{role.mention}{nl}"
    status_txt = (f"Text to show with this embed on publish: ```{client.metadata['text']}```"
                  "\n"
                  f"Roles set to ping: {roles}"
                  "\n"
                  f"Pin: {client.metadata['pin']}")
    await ctx.edit_initial_response(content=status_txt, components=[])
    await asyncio.sleep(5)


async def publish_to_channel(ctx: SlashContext, bot: hikari.GatewayBot, client: tanjun.Client):
    content_str = ""
    for role in client.metadata['roles']:
        content_str += f"{role.mention}{nl}"
    content_str += client.metadata['text']
    if content_str == "":
        content_str = "-"

    await ctx.edit_initial_response(content="What channel would you like to Publish to:", components=[])

    event = await collect_response(ctx, validator=ensure_guild_channel)

    found_channel = None
    guild = ctx.get_guild()
    channels = guild.get_channels()

    for channel_id in channels:
        channel = guild.get_channel(channel_id)
        if str(channel.id) in event.content or channel.name == event.content:
            found_channel = channel
            break

    embed_message = await found_channel.send(content=content_str, embed=client.metadata['embed'])

    if client.metadata['pin']:
        await found_channel.pin_message(embed_message)


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

    await ctx.edit_initial_response(content=f"Channel `{event.content}` not found! Try again?")
    await event.message.delete()
    await asyncio.sleep(5)


@ tanjun.as_loader
def load(client: tanjun.abc.Client) -> None:
    client.add_component(component.copy())
