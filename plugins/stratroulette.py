import collections
import hikari
import typing
import tanjun
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

attackNamesArray = generalStratNameArray + attackStratNameArray
attackStratsArray = generalStrategiesArray + attackStrategiesArray
defenseNamesArray = generalStratNameArray + defenseStratNameArray
defenseStratsArray = generalStrategiesArray + defenseStrategiesArray

component = tanjun.Component()


@component.with_slash_command
@tanjun.as_slash_command('comp', 'Gives a randomized comp')
async def comp(ctx: tanjun.abc.Context) -> None:
    global agents
    composition = {random.choice(agents)}
    while len(composition) != 5:
        composition.add(random.choice(agents))
    await ctx.respond(', '.join(composition))


@component.with_slash_command
@tanjun.as_slash_command('random-player-selector', 'Chooses a random player')
async def random_player_selector(ctx: tanjun.abc.Context) -> None:
    randomplayer = random.choice(
        ['Top Frag', '2nd Frag', '3rd Frag', '4th Frag', 'Bottom Frag']
    )
    await ctx.respond(randomplayer)


@component.with_slash_command
@tanjun.as_slash_command('attack-strat', 'Strategy when playing attack')
async def attack_strat(ctx: tanjun.abc.Context) -> None:
    global acount, attackStratsArray, attackNamesArray
    roll, acount = stratChoice(attackNamesArray, attackStratsArray, acount)
    await ctx.respond(roll)


@tanjun.as_loader
def load_module(client: tanjun.abc.Client) -> None:
    client.add_component(component.copy())


@tanjun.as_unloader
def unload_component(client: tanjun.abc.Client) -> None:
    client.remove_component_by_name(component.name)
