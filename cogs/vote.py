"""Vote Commands"""
from discord.ext import commands
from discord import Embed, emoji, message
from discord import Colour
from discord.ext.commands import context
import json
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice


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
                           required=True)
                       ])
    @commands.has_permissions(send_messages=True)
    async def vote(self, ctx, title, options):
        """Sets up a vote that can be reacted to.\t Arguments: title, options(multiple: at least 2)"""
        options = options.split()
        if len(options) < 2 or len(options) > 10:
            await ctx.send("There must be at least 2 and no more than 10 options to vote")
            return

        emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣",
                  "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

        options = [
            f"**{i+1}. {options[i]}:\t**`0`" for i in range(len(options))]
        contents = "\n".join(options)
        embed = Embed(
            title=title,
            description=f"{ctx.author} started a vote.\n{contents}",
            colour=Colour.orange()
        )

        embed.set_footer(text='React below to vote')
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)

        msg = await ctx.send(embed=embed)

        for i in range(len(options)):
            await msg.add_reaction(emojis[i])

        with open("json_files/vote.json") as json_read:
            data = json.load(json_read)

            new_vote = {
                "message_id": msg.id,
                "channel_id": msg.channel.id
            }

            data.append(new_vote)

        with open("json_files/vote.json", "w") as json_write:
            json.dump(data, json_write, indent=4)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """React when a reaction is added"""
        if payload.member.bot:
            pass

        else:

            with open("json_files/vote.json") as event_file:

                data = json.load(event_file)
                for i in data:
                    if i['message_id'] == payload.message_id:
                        emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣",
                                  "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
                        index = emojis.index(payload.emoji.name) + 1
                        channel = self.client.get_channel(id=i['channel_id'])
                        msg = await channel.fetch_message(id=i['message_id'])
                        new_embed = msg.embeds[0]
                        contents = new_embed.description.split("\n")
                        contents[index] = contents[index][:contents[index].find(
                            "`")+1] + str(int(contents[index][contents[index].find("`")+1:-1])+1) + "`"
                        new_embed.description = "\n".join(contents)
                        await msg.edit(embed=new_embed)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        """Reacts when a reaction is removed"""
        with open("json_files/vote.json") as event_file:

            data = json.load(event_file)
            for i in data:
                if i['message_id'] == payload.message_id:
                    emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣",
                              "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
                    index = emojis.index(payload.emoji.name) + 1
                    channel = self.client.get_channel(id=i['channel_id'])
                    msg = await channel.fetch_message(id=i['message_id'])
                    new_embed = msg.embeds[0]
                    contents = new_embed.description.split("\n")
                    contents[index] = contents[index][:contents[index].find(
                        "`")+1] + str(int(contents[index][contents[index].find("`")+1:-1])-1) + "`"
                    new_embed.description = "\n".join(contents)
                    await msg.edit(embed=new_embed)


def setup(client):
    client.add_cog(Vote(client))
