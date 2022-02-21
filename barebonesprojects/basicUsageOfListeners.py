import hikari
import tanjun

component = tanjun.Component()


@component.with_listener(hikari.MessageCreateEvent)
async def on_message_create(event: hikari.MessageCreateEvent):
    if event.is_human:
        chan = event.channel_id
        print(chan)
        print(event.content)
        await event.message.respond('big jean bussy')
