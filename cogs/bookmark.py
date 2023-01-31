"""Imports"""
import discord
from discord.ext import commands
import datetime

class Bookmark(commands.Cog):
    """Bookmark commands"""

    def __init__(self, bot):
        self.bot:commands.Bot = bot

    async def cog_before_invoke(self, ctx):
        """
        Triggers typing indicator on Discord before every command.
        """
        await ctx.trigger_typing()    
        return
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self,payload):
        bookmark_emoji = discord.PartialEmoji.from_str("🔖")
        emoji = payload.emoji
        chan_id = payload.channel_id
        msg_id = payload.message_id
        channel = await self.bot.fetch_channel(chan_id)
        msg = await channel.fetch_message(msg_id)
        member:discord.Member = payload.member
        if isinstance(channel,discord.channel.DMChannel) == False:
            if emoji == bookmark_emoji:
                attachments = msg.attachments
                embed = discord.Embed(color=discord.Color.from_rgb(179,95,248),timestamp=datetime.datetime.now())        
                embed.set_author(name=msg.author.name,icon_url=msg.author.display_avatar)
                embed.description = msg.content[:4096]
                embed.add_field(name="Jump",value=f"[Go to Message!]({msg.jump_url})")
                embed.set_footer(text=f"Guild: {channel.guild.name} | Channel #{channel.name}")
                attac = ""
                if not attachments == []:
                    img_added = False
                    for attachment in attachments:
                        if img_added == False:
                            if attachment.content_type in ["image/avif","image/jpeg","image/png"]:
                                try:
                                    embed.set_image(url=attachment.url)
                                except:
                                    pass
                                img_added= True

                        attac+=f"{attachment.url}\n"     

                sent = await member.send(content=f"Message Bookmarked !\n{attac}",embed=embed)
                await sent.add_reaction("❌")
            
            del_emoji = discord.PartialEmoji.from_str("❌")
            if emoji == del_emoji and msg.author.id == self.bot.user.id and payload.user_id != self.bot.user.id:
                await msg.delete()
        
        if isinstance(channel,discord.channel.DMChannel) == True:
            del_emoji = discord.PartialEmoji.from_str("❌")
            if emoji == del_emoji and msg.author.id == self.bot.user.id and payload.user_id != self.bot.user.id:
                await msg.delete()



def setup(bot):
    bot.add_cog(Bookmark(bot))
    print("Bookmark cog is loaded")