import hikari
import tanjun

component = tanjun.Component()


@component.with_listener(hikari.MessageCreateEvent)
async def on_message(event: hikari.MessageCreateEvent):
    sunnylink = 'Go follow my soundcloud at https://soundcloud.com/sunnyakt'
    if event.is_human:
        msg = event.content
        if type(msg) == str:
            msg = msg.lower()
            if 'soundcloud' in msg:
                await event.message.respond(sunnylink)


@tanjun.as_loader
def load_module(client: tanjun.abc.Client) -> None:
    client.add_component(component.copy())


@tanjun.as_unloader
def unload_component(client: tanjun.abc.Client) -> None:
    client.remove_component_by_name(component.name)
