"""Main"""
import discord
from discord import client
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext

import os
import time


client = commands.Bot(command_prefix='.')
slash = SlashCommand(client, sync_commands=True)


@client.event
async def on_ready():
    print(f"logged in at {time.ctime(time.time())} as {client.user}")



@slash.slash(name="hi",
            description="Says Hello!!")
async def hi(ctx):
    """Says Hello!!.\tArguments: None"""
    await ctx.send("Hello!!")


@slash.slash(name="latency",
            description="Measures the bot ping.")
async def latency(ctx):
    """Measures the bot ping.\tArguments: None"""
    await ctx.send(f"latency is around {round(client.latency * 1000)} ms.")


@client.command()
async def load(ctx, extension):
    """Loads a cog extension.\tArguments: extension"""
    client.load_extension(f"cogs.{extension}")
    await ctx.send(f"Loaded the {extension} cog")


@client.command()
async def unload(ctx, extension):
    """Loads a cog extension.\tArguments: extension"""
    client.unload_extension(f"cogs.{extension}")
    await ctx.send(f"Unloaded the {extension} cog")


@client.command()
async def reload(ctx, extension):
    """Reloads a cog extension.\tArguments: extension"""
    client.unload_extension(f"cogs.{extension}")
    client.load_extension(f"cogs.{extension}")
    await ctx.send(f"Reloaded the {extension} cog")


for file in os.listdir("./cogs"):
    if file.endswith(".py"):
        client.load_extension(f"cogs.{file[:-3]}")

client.run(os.getenv('DISCORD_TOKEN'))
