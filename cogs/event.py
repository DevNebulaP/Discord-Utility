"""Event Commands"""
from discord import Colour
from discord.ext import commands
from discord import Embed
from discord_slash import cog_ext
import discord_slash
from discord_slash.utils.manage_commands import create_option

from discord_slash.context import MenuContext
from discord_slash.model import ContextMenuType, ButtonStyle
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.utils.manage_components import create_select, create_select_option


class Event(commands.Cog):

    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(name="event",
                       description="Proposes an event that can be reacted to.",
                       options=[create_option(
                           name="title",
                           description="The title of the event.",
                           option_type=3,
                           required=True),
                           create_option(
                           name="content",
                           description="The content of the event.",
                           option_type=3,
                           required=False)
                       ])
    @commands.has_permissions(send_messages=True)
    async def event(self, ctx, title, content=""):
        """Proposes an event that can be reacted to.\t Arguments: title"""
        embed = Embed(
            title=title,
            description=content,
            colour=Colour.green()
        )

        embed.set_footer(
            text='Use the button below to react, press again to remove.')
        embed.set_author(name=ctx.author.display_name,
                         icon_url=ctx.author.avatar_url)
        embed.add_field(name="Accepted", value=None, inline=True)
        embed.add_field(name="Declined", value=None, inline=True)
        embed.add_field(name="Maybe", value=None, inline=True)

        buttons = [
            create_button(
                style=ButtonStyle.green,
                label="Accept",
                custom_id="event_accept",
            ),
            create_button(
                style=ButtonStyle.red,
                label="Decline",
                custom_id="event_decline",
            ),
            create_button(
                style=ButtonStyle.gray,
                label="Maybe",
                custom_id="event_maybe",
            )
        ]
        action_row = create_actionrow(*buttons)

        await ctx.send(embed=embed, components=[action_row])

    @cog_ext.cog_component()
    async def event_accept(self, ctx: discord_slash.ComponentContext):
        try:
            embed = ctx.origin_message.embeds[0]
        except IndexError:
            return
        field = embed.fields[0].value.split("\n")
        if ctx.author.mention in field:
            field.remove(ctx.author.mention)
        else:
            if field == ["None"]:
                field = []
            field.append(ctx.author.mention)
        if not len(field):
            field = ["None"]
        embed.set_field_at(
            index=0, name="Accepted", value="\n".join(field))
        await ctx.edit_origin(embed=embed)

    @cog_ext.cog_component()
    async def event_decline(self, ctx: discord_slash.ComponentContext):
        try:
            embed = ctx.origin_message.embeds[0]
        except IndexError:
            return
        field = embed.fields[1].value.split("\n")
        if ctx.author.mention in field:
            field.remove(ctx.author.mention)
        else:
            if field == ["None"]:
                field = []
            field.append(ctx.author.mention)
        if not len(field):
            field = ["None"]
        embed.set_field_at(
            index=1, name="Declined", value="\n".join(field))
        await ctx.edit_origin(embed=embed)

    @cog_ext.cog_component()
    async def event_maybe(self, ctx: discord_slash.ComponentContext):
        try:
            embed = ctx.origin_message.embeds[0]
        except IndexError:
            return
        field = embed.fields[2].value.split("\n")
        if ctx.author.mention in field:
            field.remove(ctx.author.mention)
        else:
            if field == ["None"]:
                field = []
            field.append(ctx.author.mention)
        if not len(field):
            field = ["None"]
        embed.set_field_at(
            index=2, name="Maybe", value="\n".join(field))
        await ctx.edit_origin(embed=embed)

    @cog_ext.cog_slash(name="button",
                       description="test buttons and action rows.")
    @commands.has_permissions(send_messages=True)
    async def button(self, ctx):
        buttons = [
            create_button(
                style=ButtonStyle.green,
                label="A Green Button",
                custom_id="button_callback",
            ),
        ]
        action_row = create_actionrow(*buttons)
        await ctx.send("Test", components=[action_row])

    @cog_ext.cog_component()
    async def button_callback(self, ctx: discord_slash.ComponentContext):
        await ctx.edit_origin(content="You've pressed a button.")

    @cog_ext.cog_slash(name="select",
                       description="test select menu.")
    @commands.has_permissions(send_messages=True)
    async def select(self, ctx):
        select = create_select(
            options=[  # the options in your dropdown
                create_select_option("Lab Coat", value="coat", emoji="🥼"),
                create_select_option("Test Tube", value="tube", emoji="🧪"),
                create_select_option("Petri Dish", value="dish", emoji="🧫")
            ],
            # the placeholder text to show when no options have been chosen
            placeholder="Choose your option",
            min_values=1,  # the minimum number of options a user must select
            max_values=2,  # the maximum number of options a user can select
            custom_id="select_callback"
        )

        # like action row with buttons but without * in front of the variable
        await ctx.send("test", components=[create_actionrow(select)])

    @cog_ext.cog_component()
    async def select_callback(self, ctx: discord_slash.ComponentContext):
        await ctx.send(content=f"You've selected {ctx.selected_options}")

    @cog_ext.cog_context_menu(target=ContextMenuType.MESSAGE,
                              name="context_menu")
    async def commandname(self, ctx: MenuContext):
        await ctx.send(
            content=f"Responded! The content of the message targeted: {ctx.target_message.content}",
            hidden=False
        )


def setup(client):
    client.add_cog(Event(client))
