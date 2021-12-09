"""Music Commands"""
import discord
from discord.ext import commands
from discord import Embed, Colour

from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option

import youtube_dl
from requests import get

import time


class Music(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.audio_queue = {}
        self.is_playing = {}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                               'options': '-vn'}
        self.YDL_OPTIONS = {'format': 'bestaudio'}

    @cog_ext.cog_slash(name="stop",
                       description="Stops the audio and disconnects the bot.")
    @commands.has_permissions(send_messages=True)
    async def stop(self, ctx):
        self.audio_queue[ctx.guild.id].clear()
        self.is_playing[ctx.guild.id] = False
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

        if ctx.guild.id in self.audio_queue:
            self.audio_queue[ctx.guild.id].append([info, source])
        else:
            self.audio_queue[ctx.guild.id] = [[info, source]]
            self.is_playing[ctx.guild.id] = False

        webpage_url = info['webpage_url']
        await ctx.send(f"Added {webpage_url} to the queue.")

        if not self.is_playing[ctx.guild.id]:
            self.is_playing[ctx.guild.id] = True
            await self.play_audio(ctx)

    async def play_audio(self, ctx):
        if len(self.audio_queue[ctx.guild.id]):
            source = self.audio_queue[ctx.guild.id][0][1]
            del self.audio_queue[ctx.guild.id][0]

            vc = ctx.voice_client
            vc.play(source, after=lambda _: self.play_next(ctx))
        else:
            self.is_playing[ctx.guild.id] = False

    def play_next(self, ctx):
        if len(self.audio_queue[ctx.guild.id]):
            source = self.audio_queue[ctx.guild.id][0][1]
            del self.audio_queue[ctx.guild.id][0]

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
        if ctx.voice_client is None:
            await ctx.send("Bot is not connected to a voice channel.")
            return
        elif voice_channel != ctx.voice_client.channel:
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
        if ctx.voice_client is None:
            await ctx.send("Bot is not connected to a voice channel.")
            return
        elif voice_channel != ctx.voice_client.channel:
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
        if ctx.voice_client is None:
            await ctx.send("Bot is not connected to a voice channel.")
            return
        elif voice_channel != ctx.voice_client.channel:
            await ctx.send("You are not in the same channel as the bot.")
            return
        ctx.voice_client.stop()
        await ctx.send("Skipped ⏭️")

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

    @cog_ext.cog_slash(name="queue",
                       description="Shows the queue of audio tracks")
    @commands.has_permissions(send_messages=True)
    async def queue(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("You are not connected to a voice channel.")
            return
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await ctx.send("Bot is not connected to a voice channel.")
            return
        elif voice_channel != ctx.voice_client.channel:
            await ctx.send("You are not in the same channel as the bot.")
            return
        embed = Embed(title="Audio Queue 💿",
                      description="You can add audio tracks using the /play command",
                      colour=Colour.purple())
        try:
            data = [i[0] for i in self.audio_queue[ctx.guild.id]]
        except KeyError:
            await ctx.send("The queue is empty")
            return

        if len(data):
            title = [f"`{i}`" for i in range(1, len(data)+1)]
            embed.add_field(name="#", value="\n".join(title), inline=True)
            title = [i['title'] for i in data]
            embed.add_field(name="Title", value="\n".join(title), inline=True)
            duration = [time.strftime(
                "%H:%M:%S", time.gmtime(i['duration'])) for i in data]
            embed.add_field(name="Duration", value="\n".join(
                duration), inline=True)
            await ctx.send(embed=embed)
        else:
            await ctx.send("The queue is empty")

    @cog_ext.cog_slash(name="queue_remove",
                       description="Remove a track from the queue",
                       options=[create_option(name="number",
                                              description="The number of the audio you want to remove in the queue.",
                                              option_type=4,
                                              required=True)
                                ])
    @commands.has_permissions(send_messages=True)
    async def queue_remove(self, ctx, number):
        if ctx.author.voice is None:
            await ctx.send("You are not connected to a voice channel.")
            return
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await ctx.send("Bot is not connected to a voice channel.")
            return
        elif voice_channel != ctx.voice_client.channel:
            await ctx.send("You are not in the same channel as the bot.")
            return

        try:
            removed = self.audio_queue[ctx.guild.id][number-1][0]['title']
            self.audio_queue[ctx.guild.id].pop(number-1)
            await ctx.send(f"Removed {removed} from the queue.")
        except (KeyError, IndexError):
            await ctx.send("Cannot remove that")

    @cog_ext.cog_slash(name="queue_clear",
                       description="Clear the audio queue.")
    @commands.has_permissions(send_messages=True)
    async def queue_clear(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("You are not connected to a voice channel.")
            return
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await ctx.send("Bot is not connected to a voice channel.")
            return
        elif voice_channel != ctx.voice_client.channel:
            await ctx.send("You are not in the same channel as the bot.")
            return

        try:
            if len(self.audio_queue[ctx.guild.id]):
                self.audio_queue[ctx.guild.id] = []
                await ctx.send("Cleared the queue.")
            else:
                await ctx.send(f"Queue is already empty!")
        except KeyError:
            await ctx.send("Queue is already empty!")


def setup(client):
    client.add_cog(Music(client))
