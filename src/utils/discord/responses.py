from typing import Iterable, Mapping, Optional, Union

import discord
from discord.embeds import EmptyEmbed
from discord.ext import commands, menus

from utils.discord.bot import bot


class HanalonPages(menus.Menu):
    def __init__(self, context: commands.Context, pages: Iterable[Mapping]):
        """Creates an interactive list of pages."""
        super().__init__()
        self.context = context
        self.pages = pages
        self.index = 0

    async def send_initial_message(
        self, ctx: commands.Context, channel: discord.abc.Messageable
    ) -> discord.Message:
        """Sends the initial message."""
        return await self.context.send(**self.pages[self.index])

    async def go_to(self, index: int):
        """Updates HanalonPages instance to a certain page."""
        index = int(index)
        if not 0 <= index < len(self.pages):
            index %= len(self.pages)
        self.index = index
        await self.message.edit(**self.pages[self.index])

    async def validate(self, payload: discord.RawReactionActionEvent) -> bool:
        """Returns whether the bot should act on a reaction."""
        if not self.context.channel.permissions_for(self.context.me).manage_messages:
            return True
        elif payload.event_type == "REACTION_ADD":
            await self.message.remove_reaction(payload.emoji.name, payload.member)
            return True
        return False

    @menus.button("⏮️")
    async def go_first(self, payload: discord.RawReactionActionEvent):
        """Go to first page."""
        if await self.validate(payload):
            await self.go_to(0)

    @menus.button("⏪")
    async def go_back(self, payload: discord.RawReactionActionEvent):
        """Go to previous page."""
        if await self.validate(payload):
            await self.go_to(self.index - 1)

    @menus.button("⏩")
    async def go_forward(self, payload: discord.RawReactionActionEvent):
        """Go to next page."""
        if await self.validate(payload):
            await self.go_to(self.index + 1)

    @menus.button("⏭")
    async def go_last(self, payload: discord.RawReactionActionEvent):
        """Go to last page."""
        if await self.validate(payload):
            await self.go_to(-1)


class HanalonEmbed(discord.Embed):
    def __init__(
        self,
        context: commands.Context,
        title: str = EmptyEmbed,
        description: str = EmptyEmbed,
        color: Union[discord.Color, int] = bot.color,
        url: str = EmptyEmbed,
    ):
        """Creates an embed with prettifying and permissions taken care of."""
        super().__init__(title=title, description=description, color=color, url=url)
        self.timestamp = context.message.created_at
        self.set_footer(
            text=f"{context.author.name}#{context.author.discriminator}",
            icon_url=context.author.avatar_url,
        )
        self.context = context
        self.response = None

    async def respond(
        self,
        code: Optional[bool] = None,
        override: bool = False,
        destination: Optional[discord.abc.Messageable] = None,
    ):
        """Sends a response; this deals with replies and reactions, which most bot messages will use."""

        self.response = HanalonResponse(self.context, code, override, destination)

        if self.context.channel.permissions_for(self.context.me).embed_links:
            await self.response.send(embed=self)
        elif self.context.channel.permissions_for(self.context.me).manage_webhooks:
            pfp = await bot.user.avatar_url.read()
            webhook = await self.context.channel.create_webhook(
                name=self.context.guild.me.display_name,
                avatar=pfp,
                reason="I can't send embeds…",
            )
            await webhook.send(embed=self)
            await webhook.delete()

            # can't be bothered to deal with reaction logic. try/except is the simplest way to
            # handle reactions.
            try:
                await self.response.send()
            except discord.Forbidden:
                pass
        elif self.context.channel.permissions_for(self.context.me).send_messages:
            if self.title:
                title_proxy = f"**{self.title}**"
            else:
                title_proxy = ""
            message = (
                f'{title_proxy}\n{self.description if self.description else ""}\n\n'
            )
            for field in self.fields:
                message += f"*{field.name}*\n{field.value}\n\n"
            try:
                await self.response.send(message)
            except discord.Forbidden:
                pass
        else:
            raise discord.Forbidden


class HanalonResponse:
    def __init__(
        self,
        context: commands.Context,
        success: Optional[bool] = None,
        override_success: bool = False,
        destination: Optional[discord.abc.Messageable] = None,
    ):
        """Creates a response to a message."""
        self.context = context
        self.success = success
        self.override = override_success
        self.destination = destination
        self.reply = None

    async def send(self, **kwargs):
        """Sends a response; this deals with replies and reactions, which most bot messages will use."""
        if "mention_author" not in kwargs:
            kwargs["mention_author"] = False
        try:
            if (
                isinstance(self.destination, discord.abc.Messageable)
                and self.destination != self.context.channel
            ):
                self.reply = await self.destination.send(**kwargs)
            else:
                self.reply = await self.context.reply(**kwargs)
        except Exception:
            if not self.override:
                raise
        if self.success:
            await self.context.message.add_reaction(bot.success)
        elif self.success is not None:
            await self.context.message.add_reaction(bot.failure)
