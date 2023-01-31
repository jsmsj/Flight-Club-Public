"""Imports"""
import discord
from discord.ext import commands
import cogs._secrets as secrets
from cogs._helpers import get_all_tiktok_urls_from_msg,generate_tiktok_embed_and_file
import datetime

class General(commands.Cog):
    """General commands"""

    def __init__(self, bot):
        self.bot:commands.Bot = bot

    async def cog_before_invoke(self, ctx):
        """
        Triggers typing indicator on Discord before every command.
        """
        await ctx.trigger_typing()    
        return
    
    @commands.Cog.listener()
    async def on_message(self,message:discord.Message):
        if message.author.bot:return
        tiktok_urls = get_all_tiktok_urls_from_msg(message.content)
        if len(tiktok_urls)!=0:
            all_sent = []
            temp = await message.reply('Working on it ....')
            for tiktok_url in tiktok_urls:
                video_file,embed = generate_tiktok_embed_and_file(message.author.name,message.author.discriminator,message.author.display_avatar.url,tiktok_url)
                if video_file and embed:
                    try:
                        await message.channel.send(file=video_file,embed=embed)
                        all_sent.append(True)
                    except Exception as e:
                        exception_msg = await message.channel.send(f"Error embedding tiktok, video size exceeds 8mb.... \n`{e}`")
                        await exception_msg.add_reaction('❌')
                        all_sent.append(False)
                else:
                    all_sent.append(False)
            await temp.delete()
            if len(tiktok_urls) == 1 and False not in all_sent and tiktok_urls[0] == message.content: 
                await message.delete()



    @commands.command()
    async def ping(self,ctx):
        await ctx.send(f'🏓 Pong ! Latency: {round(self.bot.latency*1000,2)}ms')
    
    @commands.command()
    async def about(self,ctx):
        em = discord.Embed(description=f"A bot for this awesome server. Run `{secrets.prefix}help` to get to know about my commands.\nIf you come across a bug or have suggestions for improvement, contact <@!713276935064649792>",color=discord.Color.from_rgb(179,95,248),timestamp=datetime.datetime.now())
        em.set_thumbnail(url="https://i.imgur.com/hb1kjTN.png")
        em.add_field(name="Version",value="`1.0.0`")
        em.add_field(name="Language",value="`English`")
        em.add_field(name="Prefix",value=f"`{secrets.prefix}`")
        em.add_field(name="Default Status",value="Streaming `Fight Club`")
        em.add_field(name="Repository Url",value="[Github](https://github.com/jsmsj/NOT-cycbot)")
        em.add_field(name="Bot Library",value="Python : [Py-cord](https://pycord.dev/)")
        em.set_footer(text="Developed by jsmsj#5252")
        await ctx.send(embed=em)

def setup(bot):
    bot.add_cog(General(bot))
    print("General cog is loaded")