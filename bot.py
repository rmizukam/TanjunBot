import os
from pathlib import Path
import hikari
import tanjun
import typing
import time
from dotenv import load_dotenv
load_dotenv()

bot = hikari.GatewayBot(os.environ.get('BOTTOKEN'))

client = tanjun.Client.from_gateway_bot(bot,
                                        declare_global_commands=[
                                            os.environ.get('GUILDTOKEN')
                                            ],
                                        mention_prefix=True
                                        )

component = tanjun.Component()
client.add_component(component)
client.load_modules('plugins.utilities')
client.load_modules('plugins.eightball')
client.load_modules('plugins.hyoonListener')
client.load_modules('plugins.sunnybot')
client.load_modules('plugins.yourmomcounter')
client.load_modules('plugins.summons')
client.load_modules('plugins.valbot')


@component.with_command
@tanjun.with_user_slash_option("user",
                               "The user facing command option's description",
                               default=None)
@tanjun.as_slash_command("hello", "The command's user facing description")
async def hello(ctx: tanjun.abc.Context,
                user: typing.Optional[hikari.User]) -> None:
    user = user or ctx.author
    await ctx.respond(f"Hello, {user}!")


bot.run()
