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

    @cog_ext.cog_slash(name="stop",
                       description="Stops the audio and disconnects the bot.")
    @commands.has_permissions(send_messages=True)
    async def stop(self, ctx):
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
            await ctx.send(f"Bot joined {voice_channel.name}")
        elif voice_channel != ctx.voice_client.channel:
            await ctx.voice_client.move_to(voice_channel)
            await ctx.send(f"Bot moved to {voice_channel.name}")

        ctx.voice_client.stop()
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                          'options': '-vn'}
        YDL_OPTIONS = {'format': 'bestaudio'}
        vc = ctx.voice_client

        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            try:
                get(video)
            except:
                info = ydl.extract_info(f"ytsearch:{video}", download=False)[
                    'entries'][0]
            else:
                info = ydl.extract_info(video, download=False)
            url = info['formats'][0]['url']
            source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
            vc.play(source)
            if 'webpage_url' in info:
                await ctx.send(f"Playing {info['webpage_url']}")
            else:
                await ctx.send(f"Playing {video}")

    @cog_ext.cog_slash(name="pause",
                       description="Pauses the audio.")
    @commands.has_permissions(send_messages=True)
    async def pause(self, ctx):
        ctx.voice_client.pause()
        await ctx.send("Paused ⏸️")

    @cog_ext.cog_slash(name="resume",
                       description="Resumes the audio.")
    @commands.has_permissions(send_messages=True)
    async def resume(self, ctx):
        ctx.voice_client.resume()
        await ctx.send("Resumed ▶️")


def setup(client):
    client.add_cog(Music(client))
