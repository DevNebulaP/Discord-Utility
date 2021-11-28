"""Event Commands"""
from discord import Colour
from discord.ext import commands
from discord import Embed
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option
import json


class Event(commands.Cog):

    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(name="event",
                       description="Proposes an event that can be reacted to.",
                       options=[create_option(
                           name="title",
                           description="The title of the event.",
                           option_type=3,
                           required=True)
                       ])
    @commands.has_permissions(send_messages=True)
    async def event(self, ctx, *, title):
        """Proposes an event that can be reacted to.\t Arguments: title"""
        embed = Embed(
            title=title,
            description=f"{ctx.author} has proposed an event.",
            colour=Colour.green()
        )

        embed.set_footer(text='React below to respond to this event invite')
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        embed.add_field(name="Accepted", value=None, inline=True)
        embed.add_field(name="Declined", value=None, inline=True)
        embed.add_field(name="Maybe", value=None, inline=True)

        msg = await ctx.send(embed=embed)
        await msg.add_reaction('✅')
        await msg.add_reaction('❌')
        await msg.add_reaction('❔')

        with open("json_files/event.json") as json_read:
            data = json.load(json_read)

            new_event = {
                "message_id": msg.id,
                "channel_id": msg.channel.id
            }

            data.append(new_event)

        with open("json_files/event.json", "w") as json_write:
            json.dump(data, json_write, indent=4)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """React when a reaction is added"""
        if payload.member.bot:
            pass

        else:

            with open("json_files/event.json") as event_file:

                data = json.load(event_file)
                for i in data:
                    if i['message_id'] == payload.message_id:
                        channel = self.client.get_channel(id=i['channel_id'])
                        msg = await channel.fetch_message(id=i['message_id'])
                        new_embed = msg.embeds[0]
                        if payload.emoji.name == "✅":
                            field = new_embed.fields[0].value
                            if field == "None":
                                field = ""
                            new_embed.set_field_at(
                                index=0, name="Accepted", value=field+"\n"+payload.member.name)
                        elif payload.emoji.name == "❌":
                            field = new_embed.fields[1].value
                            if field == "None":
                                field = ""
                            new_embed.set_field_at(
                                index=1, name="Declined", value=field+"\n"+payload.member.name)
                        elif payload.emoji.name == "❔":
                            field = new_embed.fields[2].value
                            if field == "None":
                                field = ""
                            new_embed.set_field_at(
                                index=2, name="Maybe", value=field+"\n"+payload.member.name)
                        await msg.edit(embed=new_embed)
                        return

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        """Reacts when a reaction is removed"""
        with open("json_files/event.json") as event_file:

            data = json.load(event_file)
            for i in data:
                if i['message_id'] == payload.message_id:
                    channel = self.client.get_channel(id=i['channel_id'])
                    msg = await channel.fetch_message(id=i['message_id'])
                    new_embed = msg.embeds[0]
                    user = await self.client.fetch_user(payload.user_id)
                    if payload.emoji.name == "✅":
                        field = new_embed.fields[0].value
                        field = field.split("\n")
                        field.remove(user.name)
                        if not len(field):
                            field = ["None"]
                        new_embed.set_field_at(
                            index=0, name="Accepted", value="\n".join(field))
                    elif payload.emoji.name == "❌":
                        field = new_embed.fields[1].value
                        field = field.split("\n")
                        field.remove(user.name)
                        if not len(field):
                            field = ["None"]
                        new_embed.set_field_at(
                            index=1, name="Declined", value="\n".join(field))
                    elif payload.emoji.name == "❔":
                        field = new_embed.fields[2].value
                        field = field.split("\n")
                        field.remove(user.name)
                        if not len(field):
                            field = ["None"]
                        new_embed.set_field_at(
                            index=2, name="Maybe", value="\n".join(field))
                    await msg.edit(embed=new_embed)
                    return


def setup(client):
    client.add_cog(Event(client))
