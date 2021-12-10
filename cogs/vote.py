"""Vote Commands"""
from discord.ext import commands
from discord import Embed, Colour
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_components import create_select, create_select_option, create_actionrow


class Vote(commands.Cog):

    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(name="vote",
                       description="Sets up a vote that can be reacted to.",
                       options=[create_option(
                           name="title",
                           description="The title of the vote.",
                           option_type=3,
                           required=True),
                           create_option(
                           name="options",
                           description="The choices that members can vote for. (multiple) separated by space.",
                           option_type=3,
                           required=True),
                           create_option(
                           name="content",
                           description="The content of the vote.",
                           option_type=3,
                           required=False),
                       ])
    @commands.has_permissions(send_messages=True)
    async def vote(self, ctx, title, options, content=""):
        """Sets up a vote that can be reacted to.\t Arguments: title, options(multiple: at least 2)"""
        options = options.split()

        select = create_select(
            options=[create_select_option(options[i], value=str(i))
                     for i in range(len(options))],
            placeholder="Cast your vote",
            min_values=1,
            max_values=len(options),
            custom_id="vote_callback"
        )
        action_row = create_actionrow(select)

        embed = Embed(
            title=title,
            description=content,
            colour=Colour.orange()
        )

        embed.set_footer(text='Select below to vote, select again to remove.')
        embed.set_author(name=ctx.author.display_name,
                         icon_url=ctx.author.avatar_url)
        for option in options:
            embed.add_field(name=f"{option}: `0`", value="None", inline=True)

        await ctx.send(embed=embed, components=[action_row])

    @cog_ext.cog_component()
    async def vote_callback(self, ctx: discord_slash.ComponentContext):
        try:
            embed: Embed = ctx.origin_message.embeds[0]
        except IndexError:
            return
        for i in ctx.selected_options:
            field = embed.fields[int(i)]
            field_values = field.value.split("\n")
            if ctx.author.mention in field_values:
                field_values.remove(ctx.author.mention)
            else:
                if field_values == ["None"]:
                    field_values = []
                field_values.append(ctx.author.mention)
            if not len(field_values):
                field_values = ["None"]
            count = len(field_values) if field_values != ["None"] else 0
            embed.set_field_at(
                index=int(i), name="".join(field.name.split(":")[:-1]) + f": `{count}`", value="\n".join(field_values))
        await ctx.edit_origin(embed=embed)


def setup(client):
    client.add_cog(Vote(client))
