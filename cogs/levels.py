"""Imports"""
import discord
from discord.ext import commands
import cogs._db_funcs as dbf


from cogs._helpers import get_hundred_levels,generate_rank_card

class Levels(commands.Cog):
    """Levels commands"""

    def __init__(self, bot):
        self.bot = bot

    async def cog_before_invoke(self, ctx):
        """
        Triggers typing indicator on Discord before every command.
        """
        await ctx.trigger_typing()    
        return

    @commands.command()
    async def rank(self,ctx:commands.Context,member:discord.Member=None):
        if not member:member=ctx.author
        levels = await get_hundred_levels(member.guild.id)
        pos = None
        details = None
        for idx,i in enumerate(levels):
            if i['userId'] == str(member.id):
                details = i
                pos = idx
        if not details: return await ctx.send("You aren't in top 100, so i do not have level data for you :(")

        rank_card = await generate_rank_card(pos+1,details,member.id)

        await ctx.send(file=rank_card)

    @commands.command()
    async def set(self,ctx):
        await ctx.send("By using these commands you can customise your rank card ! . the list of commands is given below:\n```\n>set_background https://url.that.leads.to.an.image.com/whatever.png\n>set_foreground https://url.that.leads.to.an.image.com/whatever.png\n>set_primary #00fa81\n>set_secondary #F91AFF\n>set_tertiary #1EAAFF\n>set_quaternary #32E1FF\n```\nColor Legend: https://i.imgur.com/zEsFeQ4.png")

    @commands.command()
    async def set_background(self,ctx,url=None):
        if not url: return await ctx.send(f"No Image Url provided !. Correct Usage: >{ctx.command.name} <https://url.that.leads.to.an.image.com/whatever.png>")
        await dbf.update_one_thing_level_img(ctx.author.id,"back",url)
        await ctx.send('Updated Background Image for your rank card to given image url')
    
    @commands.command()
    async def set_foreground(self,ctx,url=None):
        if not url: return await ctx.send(f"No Image Url provided !. Correct Usage: >{ctx.command.name} <https://url.that.leads.to.an.image.com/whatever.png>")
        await dbf.update_one_thing_level_img(ctx.author.id,"fore",url)
        await ctx.send('Updated Foreground Image for your rank card to given image url')

    @commands.command()
    async def set_primary(self,ctx,color=None): 
        if not color: return await ctx.send(f"No HEX Color provided !. Correct Usage: >{ctx.command.name} #00fa81\nColor Legend: https://i.imgur.com/zEsFeQ4.png")
        await dbf.update_one_thing_level_img(ctx.author.id,"prim",color)
        await ctx.send('Updated Primary Color for your rank card.')
    
    @commands.command()
    async def set_secondary(self,ctx,color=None): 
        if not color: return await ctx.send(f"No HEX Color provided !. Correct Usage: >{ctx.command.name} #F91AFF\nColor Legend: https://i.imgur.com/zEsFeQ4.png")
        await dbf.update_one_thing_level_img(ctx.author.id,"second",color)
        await ctx.send('Updated Secondary Color for your rank card.')

    @commands.command(aliases=['set_tert','set_terti'])
    async def set_tertiary(self,ctx,color=None): 
        if not color: return await ctx.send(f"No HEX Color provided !. Correct Usage: >{ctx.command.name} #1EAAFF\nColor Legend: https://i.imgur.com/zEsFeQ4.png")
        await dbf.update_one_thing_level_img(ctx.author.id,"terti",color)
        await ctx.send('Updated Tertiary Color for your rank card.')
    
    @commands.command(aliases=['set_quarternary','set_quaternery','set_quarternery','set_quat'])
    async def set_quaternary(self,ctx,color=None): 
        if not color: return await ctx.send(f"No HEX Color provided !. Correct Usage: >{ctx.command.name} #32E1FF\nColor Legend: https://i.imgur.com/zEsFeQ4.png")
        await dbf.update_one_thing_level_img(ctx.author.id,"quater",color)
        await ctx.send('Updated Quaternary Color for your rank card.')
    


def setup(bot):
    bot.add_cog(Levels(bot))
    print("Levels cog is loaded")