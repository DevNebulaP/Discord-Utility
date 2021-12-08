"""Music Commands"""
import discord
from discord.ext import commands

from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option

import youtube_dl
from requests import get


class Music(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.queue = {}
        self.is_playing = {}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                               'options': '-vn'}
        self.YDL_OPTIONS = {'format': 'bestaudio'}

    @cog_ext.cog_slash(name="stop",
                       description="Stops the audio and disconnects the bot.")
    @commands.has_permissions(send_messages=True)
    async def stop(self, ctx):
        self.queue[ctx.guild.id].clear()
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()
        await ctx.send("Audio has been stopped.")

    @cog_ext.cog_slash(name="play",
                       description="Plays an audio from a Youtube video.",
                       options=[create_option(name="video",
                                              description="The Url or the name of the video you want to be played.",
                                              option_type=3,
                                              required=True)
                                ])
    @commands.has_permissions(send_messages=True)
    async def play(self, ctx, video):
        if ctx.author.voice is None:
            await ctx.send("You are not connected to a voice channel.")
            return
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
            await ctx.send(f"Bot joined {voice_channel.name}.")
        elif voice_channel != ctx.voice_client.channel:
            await ctx.send("You are not in the same channel as the bot.")
            return

        with youtube_dl.YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                get(video)
            except:
                info = ydl.extract_info(f"ytsearch:{video}", download=False)[
                    'entries'][0]
            else:
                info = ydl.extract_info(video, download=False)
        if not len(info):
            ctx.send("Video not found!")
            return

        url = info['formats'][0]['url']
        source = await discord.FFmpegOpusAudio.from_probe(url, **self.FFMPEG_OPTIONS)

        if ctx.guild.id in self.queue:
            self.queue[ctx.guild.id].append([info, source])
        else:
            self.queue[ctx.guild.id] = [[info, source]]
            self.is_playing[ctx.guild.id] = False

        if 'webpage_url' in info:
            await ctx.send(f"Added {info['webpage_url']} to the queue.")
        else:
            await ctx.send(f"Added {video} to the queue.")

        if not self.is_playing[ctx.guild.id]:
            self.is_playing[ctx.guild.id] = True
            await self.play_audio(ctx)

    async def play_audio(self, ctx):
        if len(self.queue[ctx.guild.id]):
            source = self.queue[ctx.guild.id][0][1]
            del self.queue[ctx.guild.id][0]

            vc = ctx.voice_client
            vc.play(source, after=lambda _: self.play_next(ctx))
        else:
            self.is_playing[ctx.guild.id] = False

    def play_next(self, ctx):
        if len(self.queue):
            source = self.queue[ctx.guild.id][0][1]
            del self.queue[ctx.guild.id][0]

            vc = ctx.voice_client
            vc.play(source, after=lambda _: self.play_next(ctx))
        else:
            self.is_playing[ctx.guild.id] = False

    @cog_ext.cog_slash(name="pause",
                       description="Pauses the audio.")
    @commands.has_permissions(send_messages=True)
    async def pause(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("You are not connected to a voice channel.")
            return
        voice_channel = ctx.author.voice.channel
        if voice_channel != ctx.voice_client.channel:
            await ctx.send("You are not in the same channel as the bot.")
            return
        ctx.voice_client.pause()
        await ctx.send("Paused ⏸️")

    @cog_ext.cog_slash(name="resume",
                       description="Resumes the audio.")
    @commands.has_permissions(send_messages=True)
    async def resume(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("You are not connected to a voice channel.")
            return
        voice_channel = ctx.author.voice.channel
        if voice_channel != ctx.voice_client.channel:
            await ctx.send("You are not in the same channel as the bot.")
            return
        ctx.voice_client.resume()
        await ctx.send("Resumed ▶️")

    @cog_ext.cog_slash(name="skip",
                       description="Skips the current audio track.")
    @commands.has_permissions(send_messages=True)
    async def skip(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("You are not connected to a voice channel.")
            return
        voice_channel = ctx.author.voice.channel
        if voice_channel != ctx.voice_client.channel:
            await ctx.send("You are not in the same channel as the bot.")
            return
        ctx.voice_client.stop()
        await ctx.send("Skipped")

    @cog_ext.cog_slash(name="join",
                       description="Connects or move the bot to where the user is.")
    @commands.has_permissions(send_messages=True)
    async def join(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("You are not connected to a voice channel.")
            return
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
            await ctx.send(f"Bot joined {voice_channel.name}")
        elif voice_channel != ctx.voice_client.channel:
            await ctx.voice_client.move_to(voice_channel)
            await ctx.send(f"Bot moved to {voice_channel.name}")
        elif voice_channel == ctx.voice_client.channel:
            await ctx.send(f"Bot is already at {voice_channel.name}")


def setup(client):
    client.add_cog(Music(client))
