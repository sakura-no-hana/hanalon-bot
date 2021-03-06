import base64
import logging
import os
import pathlib

import discord
from discord.ext import commands
from discord.ext.commands.bot import BotBase
from motor.motor_asyncio import AsyncIOMotorClient
import yaml

config_files = [pathlib.Path("../config.yaml"), pathlib.Path("config.yaml")]
config = None

if "config" in os.environ:
    config = yaml.load(
        base64.b64decode(os.environ["config"]).decode("utf-8"), Loader=yaml.CSafeLoader
    )
else:
    for config_file in config_files:
        try:
            with open(config_file, encoding="utf-8") as file:
                config = yaml.load(file, Loader=yaml.CSafeLoader)
            break
        except FileNotFoundError:
            ...

if not config:
    logging.critical("No configuration found; bot cannot start.")
    raise FileNotFoundError


def prefix(bot: BotBase, message: discord.Message) -> set[str]:
    """Returns the set of prefixes the bot accepts."""
    return {"$", f"<@{bot.user.id}> ", f"<@!{bot.user.id}> "}


intents = discord.Intents(guilds=True, messages=True, reactions=True)

bot = commands.AutoShardedBot(
    activity=discord.Activity(
        name="the Sola bot arena", type=discord.ActivityType.competing
    ),
    command_prefix=prefix,
    intents=intents,
    owner_ids=config["devs"],
    status=discord.Status.idle,
)
bot.color = config["color"]
bot.success = config["success"]
bot.failure = config["failure"]
bot.db = AsyncIOMotorClient(config["mongo"])["hanalon"]
cogs_dir = pathlib.Path("./bot/cogs")

bot.owner_only = commands.check(lambda ctx: bot.is_owner(ctx.author))

bot.__version__ = "0a (unversioned)"


def include_cog(cog: commands.Cog):
    """Loads a cog."""
    bot.add_cog(cog())


def load_cogs():
    """Loads all cogs."""
    for root, _, files in os.walk(cogs_dir):
        for f in files:
            if (module := cogs_dir / f).suffix == ".py":
                bot.load_extension(
                    f"{'.'.join(pathlib.Path(root).parts)}.{module.stem}"
                )


def is_response(ctx, message, response):
    try:
        return (
            message.reference.message_id == response.reply.id
            and message.author == ctx.author
        )
    except AttributeError:
        return False


@bot.listen("on_ready")
async def prepare():
    """Prints to stdout when bot logs on."""
    print(f"Logged on as {bot.user.name}#{bot.user.discriminator}")


@bot.listen("on_command_error")
async def handle(ctx: commands.Context, error: commands.CommandError):
    """Handles command errors; it currently reacts to them."""
    if not isinstance(error, commands.CommandNotFound):
        await ctx.message.add_reaction(bot.failure)
    raise error


def run(shard_id, shard_total):
    """Starts the bot."""
    load_cogs()
    if shard_id != -1:
        bot.shard_count = shard_total
        bot.shard_ids = [shard_id]
    bot.run(config["token"])
