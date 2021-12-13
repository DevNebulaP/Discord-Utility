"""Moderation Commands"""
import discord
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option


class Moderation(commands.Cog):

    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(name="channel_clear",
                       description="Clear messages in a text channel. Requires permission to manage messages.",
                       options=[create_option(
                           name="amount",
                           description="The amount of messages to clear (Default: 10).",
                           option_type=4,
                           required=False)
                       ])
    @commands.has_permissions(manage_messages=True)
    async def channel_clear(self, ctx, amount=10):
        """Clear messages.\tArguments: amount(default=10)"""
        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(f"Cleared {len(deleted)} messages")

    @cog_ext.cog_slash(name="kick",
                       description="Kick a member. Requires permission to kick a member.",
                       options=[create_option(
                           name="member",
                           description="The member you want to kick.",
                           option_type=6,
                           required=True),
                           create_option(
                           name="reason",
                           description="The reason for kicking the member.",
                           option_type=3,
                           required=False)
                       ])
    @ commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """Kicks a user.\tArguments: member, reason(optional)"""
        await member.kick(reason=reason)
        await ctx.send(f"{member.mention} has been kicked")

    @cog_ext.cog_slash(name="disconnect",
                       description="Disconnects a member from voice. Requires permission to kick a member.",
                       options=[create_option(
                           name="member",
                           description="The member you want to disconnect from voice.",
                           option_type=6,
                           required=True)
                       ])
    @ commands.has_permissions(kick_members=True)
    async def disconnect(self, ctx, member: discord.Member,):
        """Disconnects a user.\tArguments: member"""
        await member.move_to(channel=None)
        await ctx.send(f"{member.mention} has been disconnected")

    @cog_ext.cog_slash(name="ban",
                       description="Bans a member. Requires permission to ban a member.",
                       options=[create_option(
                           name="member",
                           description="The member you want to ban.",
                           option_type=6,
                           required=True),
                           create_option(
                           name="reason",
                           description="The reason for banning the member.",
                           option_type=3,
                           required=False)
                       ])
    @ commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """Bans a user.\tArguments: member, reason(optional)"""
        await member.ban(reason=reason)
        await ctx.send(f"{member.mention} has been banned")

    @cog_ext.cog_slash(name="banned",
                       description="Shows a list of banned user(s). Requires permission to ban a member.")
    @ commands.has_permissions(ban_members=True)
    async def banned(self, ctx):
        """Shows banned users.\tArguments: None"""
        banned_users = await ctx.guild.bans()
        banned_users = [users.user.mention for users in banned_users]
        await ctx.send(", ".join(banned_users) if len(banned_users) else "There are no banned users.")

    @cog_ext.cog_slash(name="unban",
                       description="Unbans a user. Requires permission to ban a member.",
                       options=[create_option(
                           name="user",
                           description="The user you want to unban.",
                           option_type=3,
                           required=True)
                       ])
    @ commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, user):
        """Unbans a user.\tArguments: user"""
        banned_users = await ctx.guild.bans()
        member_name, member_num = user.split('#')

        for data in banned_users:
            user = data.user

            if (user.name, user.discriminator) == (member_name, member_num):
                await ctx.guild.unban(user)
                await ctx.send(f"{user.mention} has been unbanned.")
                return

    @cog_ext.cog_slash(name="role_give",
                       description="Gives a role to a user. Requires permission to manage roles.",
                       options=[create_option(
                           name="member",
                           description="The member you want to give a role to.",
                           option_type=6,
                           required=True),
                           create_option(
                           name="role",
                           description="The role you want to give.",
                           option_type=8,
                           required=True)
                       ])
    @ commands.has_permissions(manage_roles=True)
    async def role_give(self, ctx, member: discord.Member, role: discord.Role):
        """Gives a role to a member.\tArguments: member, role"""
        await member.add_roles(role)
        await ctx.send(f"Gave the role {role.mention} to {member.mention}")

    @cog_ext.cog_slash(name="role_strip",
                       description="Strip all roles from a member. Requires permission to manage roles.",
                       options=[create_option(
                           name="member",
                           description="The member you want to give a role to.",
                           option_type=6,
                           required=True)
                       ])
    @ commands.has_permissions(manage_roles=True)
    async def role_strip(self, ctx, member: discord.Member):
        """Removes all role(s) from a member.\tArguments: member"""
        roles = member.roles
        for role in roles:
            try:
                await member.remove_roles(role)
            except:
                pass
        await ctx.send(f"Stripped {member.mention} of thier roles.")

    @cog_ext.cog_slash(name="role_remove",
                       description="Remove a role from a member. Requires permission to manage roles.",
                       options=[create_option(
                           name="member",
                           description="The member you want to remove a role from.",
                           option_type=6,
                           required=True),
                           create_option(
                           name="role",
                           description="The role you want to remove.",
                           option_type=8,
                           required=True)
                       ])
    @ commands.has_permissions(manage_roles=True)
    async def role_remove(self, ctx, member: discord.Member, role: discord.Role):
        """Removes a role from a member.\tArguments: member, roles"""
        if role not in member.roles:
            return
        await member.remove_roles(role)
        await ctx.send(f"Removed the role {role.mention} from {member.mention}.")

    @cog_ext.cog_slash(name="channel_lock",
                       description="Lock a text channel. Requires permission to manage channels.",
                       options=[create_option(
                           name="channel",
                           description="The channel you want to lock. (Default: The channel you sent this command in)",
                           option_type=7,
                           required=False)
                       ])
    @ commands.has_permissions(manage_channels=True)
    async def channel_lock(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel

        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send(f"{channel.name} is locked.")

    @cog_ext.cog_slash(name="channel_unlock",
                       description="Unlock a text channel. Requires permission to manage channels.",
                       options=[create_option(
                           name="channel",
                           description="The channel you want to unlock. (Default: The channel you sent this command in)",
                           option_type=7,
                           required=False)
                       ])
    @ commands.has_permissions(manage_channels=True)
    async def channel_unlock(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel

        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = True
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send(f"{channel.name} is unlocked.")


def setup(client):
    client.add_cog(Moderation(client))
