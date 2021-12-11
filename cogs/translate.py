from discord.ext import commands
from discord import Embed, Colour
from discord_slash import cog_ext, MenuContext, ContextMenuType, ComponentContext
from discord_slash.utils.manage_components import create_select, create_select_option, create_actionrow

from googletrans import Translator, LANGUAGES
from googletrans.models import Translated


class Translate(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.lang = {
            'zh-cn': ['Chinese (simplified)', '🇨🇳'],
            'zh-tw': ['Chinese (traditional)', '🇹🇼'],
            'en': ['English', '🇬🇧'],
            'fr': ['French', '🇫🇷'],
            'de': ['German', '🇩🇪'],
            'it': ['Italian', '🇮🇹'],
            'ja': ['Japanese', '🇯🇵'],
            'ko': ['Korean', '🇰🇷'],
            'ru': ['Russian', '🇷🇺'],
            'es': ['Spanish', '🇪🇸'],
            'th': ['Thai', '🇹🇭'],
        }

    @cog_ext.cog_context_menu(target=ContextMenuType.MESSAGE,
                              name="translate")
    async def translate(self, ctx: MenuContext):
        if ctx.target_message.content == "":
            await ctx.send("The message you are trying to translate has no content.", hidden=True)
            return

        translator = Translator()
        translated: Translated = translator.translate(
            ctx.target_message.content)

        embed = Embed(
            title="Google Translate",
            description=f"Translating what {ctx.target_message.author.mention} said.",
            colour=Colour.teal()
        )

        select = create_select(
            options=[create_select_option(self.lang[i][0], value=str(i), emoji=self.lang[i][1])
                     for i in self.lang],
            placeholder="Select destination language.",
            min_values=1,
            max_values=1,
            custom_id="translate_callback"
        )
        action_row = create_actionrow(select)

        embed.set_footer(
            text='Select below to change the destination language.')
        embed.set_author(name=ctx.target_message.author.display_name,
                         icon_url=ctx.target_message.author.avatar_url)
        embed.add_field(name=f"Translated from {LANGUAGES[translated.src.lower()].capitalize()}",
                        value=f"***{translated.origin}***", inline=True)
        embed.add_field(name="Translated to English",
                        value=f"***{translated.text}***", inline=True)
        await ctx.send(embed=embed, components=[action_row])

    @cog_ext.cog_component()
    async def translate_callback(self, ctx: ComponentContext):
        try:
            embed: Embed = ctx.origin_message.embeds[0]
        except IndexError:
            return
        original_field = embed.fields[0]
        translator = Translator()
        translated: Translated = translator.translate(
            original_field.value, dest=ctx.selected_options[0])
        embed.set_field_at(
            index=1, name=f"Translated to {self.lang[ctx.selected_options[0]][0]}", value=f"***{translated.text}***")
        await ctx.edit_origin(embed=embed)


def setup(client):
    client.add_cog(Translate(client))
