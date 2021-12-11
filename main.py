"""Main"""
from discord import client
from discord.ext import commands
from discord_slash import SlashCommand

import os
import time


client = commands.Bot(command_prefix="du-dev.")
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


for file in os.listdir("./cogs"):
    if file.endswith(".py"):
        client.load_extension(f"cogs.{file[:-3]}")

client.run(open('token.txt').readline())
