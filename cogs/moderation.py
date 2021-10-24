"""Moderation Commands"""
import discord
from discord.ext import commands

class Moderation(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['clr'])
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount=10):
        """Clear messages.\tArguments: amount(default=10)"""
        await ctx.channel.purge(limit=amount+1)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member : discord.Member, *, reason=None):
        """Kicks a user.\tArguments: member"""
        await member.kick(reason=reason)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member : discord.Member, *, reason=None):
        """Bans a user.\tArguments: member"""
        await member.ban(reason=reason)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def banned(self, ctx):
        """Shows banned users.\tArguments: None"""
        banned_users = await ctx.guild.bans()
        banned_users = [users.user.mention for users in banned_users]
        await ctx.send(", ".join(banned_users))

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        """Unbans a user.\tArguments: member"""
        banned_users = await ctx.guild.bans()
        member_name, member_num = member.split('#')

        for user in banned_users:
            user = user.user

            if (user.name, user.discriminator) == (member_name, member_num):
                await ctx.guild.unban(user)
                await ctx.send(f"{user.mention} has been unbanned.")
                return

def setup(client):
    client.add_cog(Moderation(client))
