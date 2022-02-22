import asyncio
from attr import field
import hikari
import tanjun

from hikari import InteractionCreateEvent
from hikari.interactions.base_interactions import ResponseType
from hikari.messages import ButtonStyle

from tanjun.abc import SlashContext
import random
from functions import stratChoice, unload_csv

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
    "📋": {"title": "Attack", "style": ButtonStyle.SECONDARY},
    '🖊️': {'title': 'Defense', 'style': ButtonStyle.SECONDARY},
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
    building_embed = hikari.Embed(title="Strat Roulette",
                                  description='Click/Tap your choice below.')
    

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


async def attack(ctx: SlashContext, bot: hikari.GatewayBot, client: tanjun.Client):
    embed_dict, *_ = bot.entity_factory.serialize_embed(client.metadata['embed'])
    global dcount, dNamesArray, dStratArray
    roll, dcount = stratChoice(dNamesArray, dStratArray, dcount)
    await ctx.edit_initial_response(content=roll, components=[])
    try:
        async with bot.stream(hikari.GuildMessageCreateEvent, timeout=60).filter(('author', ctx.author)) as stream:
            async for event in stream:
                embed_dict['title'] = event.content[:200]
                client.metadata['embed'] = bot.entity_factory.deserialize_embed(embed_dict)
                await ctx.edit_initial_response(content="Title updated!", embed=client.metadata['embed'], components=[])
                await event.message.delete()
                return
    except asyncio.TimeoutError:
        await ctx.edit_initial_response("Waited for 60 seconds... Timeout.", embed=None, components=[])


async def defense(ctx: SlashContext, bot: hikari.GatewayBot, client: tanjun.Client):
    embed_dict, *_ = bot.entity_factory.serialize_embed(client.metadata['embed'])
    await ctx.edit_initial_response(content='Defense', components=[])
    async with bot.stream(hikari.GuildMessageCreateEvent, timeout=60).filter(('author', ctx.author)) as stream:
        async for event in stream:
            global acount, aNamesArray, aStratArray
            roll, acount = stratChoice(aNamesArray, aStratArray, acount)
            client.metadata['embed'] = bot.entity_factory.deserialize_embed(embed_dict)
            await ctx.edit_initial_response(content=roll, embed=client.metadata['embed'], components=[])
            await event.message.delete()
            return


# async def attack(ctx: SlashContext, bot: hikari.GatewayBot, client: tanjun.Client):
#     embed_dict, *_ = bot.entity_factory.serialize_embed(client.metadata['embed'])
#     await ctx.edit_initial_response(content='Attack', components=[])
#     async with bot.stream(hikari.GuildMessageCreateEvent, timeout=60).filter(('author', ctx.author)) as stream:
#         global dcount, dNamesArray, dStratArray
#         roll, dcount = stratChoice(dNamesArray, dStratArray, dcount)
#         await ctx.respond(roll)


@ tanjun.as_loader
def load(client: tanjun.abc.Client) -> None:
    client.add_component(component.copy())
