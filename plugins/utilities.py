import tanjun

component = tanjun.Component()


@component.with_slash_command
@tanjun.as_slash_command('whats-my-id',
                         'Find out what your user ID is',
                         default_to_ephemeral=True
                         )
async def whats_my_id(ctx: tanjun.abc.Context) -> None:
    authID = ctx.author.id
    authMention = ctx.author.mention
    await ctx.respond(f"Hi {authMention}!\nYour User ID is: '''{authID}'''")


@tanjun.as_loader
def load_module(client: tanjun.abc.Client) -> None:
    client.add_component(component.copy())


@tanjun.as_unloader
def unload_component(client: tanjun.abc.Client) -> None:
    client.remove_component_by_name(component.name)
