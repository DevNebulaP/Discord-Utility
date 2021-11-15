"""Moderation Commands"""
import discord
from discord.ext import commands
from discord import Embed
from discord import Colour
import random
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice


class Randomizer(commands.Cog):

    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(name="random",
                       description="Picks 1 result randomly from given options.",
                       options=[create_option(
                           name="title",
                           description="The title of the randomizer.",
                           option_type=3,
                           required=True),
                           create_option(
                           name="options",
                           description="The pool of possible out comes.",
                           option_type=3,
                           required=True)
                       ])
    @commands.has_permissions(send_messages=True)
    async def random(self, ctx, title, options):
        """Picks 1 result randomly from given options."""
        options = options.split()
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
