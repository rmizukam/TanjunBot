import collections
import hikari
import typing
import tanjun
import random
from functions import unload_csv

component = tanjun.Component()
response = unload_csv('./dataFiles/responses.csv', 'responses')


@component.with_command
@tanjun.with_str_slash_option(
                              "question", "Input your question here",
                              default=None
                              )
@tanjun.as_slash_command(
                         'eightball',
                         'Answers your questions',
                         default_to_ephemeral=False
                         )
async def eightball(
                    ctx: tanjun.abc.Context,
                    question: typing.Optional[str]
                    ) -> None:
    msg = f"Question: {question}\nAnswer: {random.choice(response)}"
    await ctx.respond(msg)


@tanjun.as_loader
def load_module(client: tanjun.abc.Client) -> None:
    client.add_component(component.copy())


@tanjun.as_unloader
def unload_component(client: tanjun.abc.Client) -> None:
    client.remove_component_by_name(component.name)
