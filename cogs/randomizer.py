"""Moderation Commands"""
import discord
from discord.ext import commands
from discord import Embed
from discord import Colour
import random


class Randomizer(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["rng"])
    @commands.has_permissions(send_messages=True)
    async def random(self, ctx, title, *options):
        """Picks 1 result randomly from given options"""
        if len(options) < 2:
            await ctx.send("There have to be at least 2 options")
            return

        embed = Embed(title=title,
                       description=f"{ctx.author} has randomized a result from {len(options)} options.",
                       colour=Colour.red())

        result = random.choice(options)

        options_text = "\n".join([f"*{i}*" for i in options])
        embed.add_field(name="Options", value=options_text, inline=True)
        embed.add_field(name="Result", value=f"`{result}`", inline=True)
        embed.set_footer(text=f"{result} is the chosen one.")
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Randomizer(client))
