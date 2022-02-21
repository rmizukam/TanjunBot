import hikari
import tanjun
import random
import csv
import os
from functions import unload_csv, psudoRanChoice
from dotenv import load_dotenv
load_dotenv()

animoopArray = unload_csv('./dataFiles/animoop.csv', 'content')
astonmartincrashesArray = unload_csv(
    './dataFiles/astonmartincrashes.csv',
    'content'
    )
h3ntaiArray = unload_csv('./dataFiles/h.csv', 'content')
hyoobaArray = unload_csv('./dataFiles/Hyooba.csv', 'content')
ahraArray = unload_csv('./dataFiles/Ahra.csv', 'content')
jinnyArray = unload_csv('./dataFiles/Jinny.csv', 'content')
jsumArray = unload_csv('./dataFiles/jsum.csv', 'content')
pokilinksArray = unload_csv('./dataFiles/pokilinks.csv', 'content')
tengaArray = unload_csv('./dataFiles/tenga.csv', 'content')
trollinArray = unload_csv('./dataFiles/trollin.csv', 'content')
tpbArray = unload_csv('./dataFiles/TPB.csv', 'content')
dclinksArray = unload_csv('./dataFiles/discordLinks.csv', 'content')
jahan = dclinksArray[0]
coomer_miku = dclinksArray[1]
blastx = dclinksArray[2]
jonSum = dclinksArray[3]

jeanArray = jsumArray + trollinArray
luckyArray = pokilinksArray + [coomer_miku]
chaoArray = tengaArray + [coomer_miku]
nutArray = hyoobaArray + [blastx] + ahraArray
jonArray = tpbArray + trollinArray + [coomer_miku] + [jonSum]
kevArray = astonmartincrashesArray + [coomer_miku] + ahraArray
jahanArray = h3ntaiArray + jinnyArray + animoopArray + [jahan] + [coomer_miku]
neneArray = [coomer_miku]

tjean = set()
tlucky = set()
tchao = set()
tnut = set()
tnene = set()
tjon = set()
thun = set()
tkev = set()
NSFWChannels = [int(os.getenv('SUMMONCHANNELKEY')),
                int(os.getenv('BOTTESTERCHANNELID')),
                int(os.getenv('HENTISENTIKEY'))
                ]

component = tanjun.Component()


summ = component.with_slash_command(
    tanjun.slash_command_group(
        'summon',
        'Summon the homie',
        default_to_ephemeral=False
    )
)


@summ.with_command
@tanjun.as_slash_command('chao', 'Summons Chao')
async def chao(ctx: tanjun.abc.Context) -> None:
    chaokey = os.getenv('CHAOKEY')
    string = '<@' + chaokey + '>'
    global tchao, NSFWChannels, chaoArray
    msg, tchao = psudoRanChoice(chaoArray, tchao)
    if ctx.channel_id in NSFWChannels:
        await ctx.respond(string)
        await ctx.respond(msg)
    else:
        await ctx.respond(
            string + ' Tenga Tenga Tenga'
        )


@summ.with_command
@tanjun.as_slash_command('hunie', 'Summons Jahandjob')
async def hunie(ctx: tanjun.abc.Context) -> None:
    huniekey = os.getenv('HUNIEKEY')
    string = '<@' + huniekey + '>'
    global thunie, NSFWChannels, jahanArray
    msg, thunie = psudoRanChoice(jahanArray, thunie)
    if ctx.channel_id in NSFWChannels:
        await ctx.respond(string)
        await ctx.respond(msg)
    else:
        await ctx.respond(
            string + ' Domestic Girlfriend is just hidden Incest'
        )


@summ.with_command
@tanjun.as_slash_command('jean', 'Summons Jean')
async def jean(ctx: tanjun.abc.Context) -> None:
    jeankey = os.getenv('JEANKEY')
    string = '<@' + jeankey + '>'
    global tjean, NSFWChannels, jeanArray
    msg, tjean = psudoRanChoice(jeanArray, tjean)
    if ctx.channel_id in NSFWChannels:
        await ctx.respond(string)
        await ctx.respond(msg)
    else:
        await ctx.respond(
            string + ' bust a move and quit nuttin'
        )


@summ.with_command
@tanjun.as_slash_command('jon', 'Summons Jon')
async def jon(ctx: tanjun.abc.Context) -> None:
    jonkey = os.getenv('JONKEY')
    string = '<@' + jonkey + '>'
    global tjon, NSFWChannels, jonArray
    msg, tjon = psudoRanChoice(jonArray, tjon)
    if ctx.channel_id in NSFWChannels:
        await ctx.respond(string)
        await ctx.respond(msg)
    else:
        await ctx.respond(
            string + ' The DVD gaper is callin...'
        )


@summ.with_command
@tanjun.as_slash_command('kev', 'Summons Kebin')
async def kev(ctx: tanjun.abc.Context) -> None:
    kevkey = os.getenv('KEVKEY')
    string = '<@' + kevkey + '>'
    global tkev, NSFWChannels, kevArray
    msg, tkev = psudoRanChoice(kevArray, tkev)
    if ctx.channel_id in NSFWChannels:
        await ctx.respond(string)
        await ctx.respond(msg)
    else:
        await ctx.respond(
            string + ' Audi A4 >> Any Aston Martins'
        )


@summ.with_command
@tanjun.as_slash_command('lucky', 'Summons LuckyNinjagoX')
async def lucky(ctx: tanjun.abc.Context) -> None:
    luckykey = os.getenv('LUCKYKEY')
    string = '<@' + luckykey + '>'
    global tlucky, NSFWChannels, luckyArray
    msg, tlucky = psudoRanChoice(luckyArray, tlucky)
    if ctx.channel_id in NSFWChannels:
        await ctx.respond(string)
        await ctx.respond(msg)
    else:
        await ctx.respond(
            string + ' Twitch Prime is a free sub for Poki.'
        )


@summ.with_command
@tanjun.as_slash_command('nene', 'Summons Nene')
async def nene(ctx: tanjun.abc.Context) -> None:
    nenekey = os.getenv('NENEKEY')
    string = '<@' + nenekey + '>'
    global tnene, NSFWChannels, neneArray
    msg, tnene = psudoRanChoice(neneArray, tnene)
    if ctx.channel_id in NSFWChannels:
        await ctx.respond(string)
        await ctx.respond(msg)
    else:
        await ctx.respond(
            string + ' Coomer Castle'
        )


@summ.with_command
@tanjun.as_slash_command('nut', 'Summons Nut')
async def nut(ctx: tanjun.abc.Context) -> None:
    nutkey = os.getenv('NUTKEY')
    string = '<@' + nutkey + '>'
    global tnut, NSFWChannels, nutArray
    msg, tnut = psudoRanChoice(nutArray, tnut)
    if ctx.channel_id in NSFWChannels:
        await ctx.respond(string)
        await ctx.respond(msg)
    else:
        await ctx.respond(
            string + ' Any Primers in the chat?'
        )


@tanjun.as_loader
def load_module(client: tanjun.abc.Client) -> None:
    client.add_component(component.copy())


@tanjun.as_unloader
def unload_component(client: tanjun.abc.Client) -> None:
    client.remove_component_by_name(component.name)
