import discord
from discord.ext.slash import InteractionResponseType

from .bot import bot


class HanalonEmbed(discord.Embed):
    def __init__(self, context, title=None, description=None, color=bot.color, url=None):
        super().__init__(title=title, description=description, color=color, url=url)
        self.timestamp = context.message.created_at
        self.set_footer(text=f'{context.author.name}#{context.author.discriminator}',
                        icon_url=context.author.avatar_url)
        self.context = context

    async def respond(self, code=None, override=False, destination=None):
        response = HanalonResponse(self.context, code, override, destination)

        if self.context.channel.permissions_for(self.context.me).embed_links:
            await response.send(embed=self)
        elif self.context.channel.permissions_for(self.context.me).manage_webhooks:
            pfp = await bot.user.avatar_url.read()
            webhook = await self.context.channel.create_webhook(
                name=self.context.guild.me.display_name, avatar=pfp, reason="I can't send embeds…")
            await webhook.send(embed=self)
            await webhook.delete()

            # can't be bothered to deal with reaction logic. try/except is the simplest way to
            # handle reactions.
            try:
                await response.send()
            except discord.Forbidden:
                pass
        elif self.context.channel.permissions_for(self.context.me).send_messages:
            if self.title:
                title_proxy = f'**{self.title}**'
            else:
                title_proxy = ''
            message = f'{title_proxy}\n{self.description if self.description else ""}\n\n'
            for field in self.fields:
                message += f'*{field.name}*\n{field.value}\n\n'
            try:
                await response.send(message)
            except discord.Forbidden:
                pass
        else:
            raise discord.Forbidden

    async def slash_respond(self, flags=None, rtype=InteractionResponseType.ChannelMessageWithSource):
        await HanalonResponse(self.context).slash(embed=self, flags=flags, rtype=rtype)


class HanalonResponse:
    def __init__(self, context, success=None, override_success=False, destination=None):
        self.context = context
        self.success = success
        self.override = override_success
        self.destination = destination

    async def send(self, *args, **kwargs):
        if args or kwargs:
            kwargs['mention_author'] = False
            try:
                if isinstance(self.destination, discord.abc.Messageable):
                    await self.destination.send(*args, **kwargs)
                else:
                    await self.context.reply(*args, **kwargs)
            except Exception as err:
                if not self.override:
                    raise err
        if self.success:
            await self.context.message.add_reaction(bot.success)
        elif self.success is not None:
            await self.context.message.add_reaction(bot.failure)

    async def slash(self, *args, **kwargs):
        await self.context.respond(*args, **kwargs)