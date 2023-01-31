"""Imports"""
import discord
from discord.ext import commands
import cogs._helpers as hp

class StatisticsCommands(commands.Cog):
    """StatisticsCommands commands"""

    def __init__(self, bot):
        self.bot = bot

    async def cog_before_invoke(self, ctx):
        """
        Triggers typing indicator on Discord before every command.
        """
        await ctx.trigger_typing()    
        return

    @commands.command()
    async def uploadlb(self,ctx,*,category=None):
        if category == "books-comics-manga":category = "bookscomicsmanga"
        if category:

            table_to_send = await hp.get_descending_table_for_category(category)
        else:

            table_to_send = await hp.get_overall_descending_table()

        desc = ""
        if category:
            if category == "bookscomicsmanga":
                desc+="Category: Books-Comics-Manga\n"
            else:
                desc+=f"Category: **{category.title()}**\n"
        
        desc+=f"```diff\n{table_to_send}\n```"
                

        em = discord.Embed(title="Upload Leaderboard",description=desc,color=discord.Color.from_rgb(179,95,248))
        await ctx.send(embed=em)

    @commands.command()
    async def stats(self,ctx,member:discord.Member=None):
        if not member: member = ctx.author
        joined_datetime = member.joined_at
        joined_time = joined_datetime.strftime("%a, %d %B %Y. %I:%M %p %Z.")
        desc = await hp.get_contribution_stats_for_user(member.id)
        em = discord.Embed(description=f"Contribution statistics for {member.mention}.\n**Member Since:** {joined_time}\n```py\n{desc}\n```",color = discord.Color.from_rgb(179,95,248))
        em.set_author(name=member.name,icon_url=member.display_avatar)
        await ctx.send(embed=em)
  


def setup(bot):
    bot.add_cog(StatisticsCommands(bot))
    print("StatisticsCommands cog is loaded")