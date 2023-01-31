from discord.ext import commands
import cogs._secrets as secrets
import discord
import os
import traceback


bot = commands.Bot(command_prefix=secrets.prefix, case_insensitive=True) # help_command=None,

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Streaming(platform='YouTube',name='Fight Club',game='Fight Club',url='https://www.youtube.com/watch?v=_pQ9XOPYvIk'))
    print("Bot is ready!")

@bot.event
async def on_command_error(ctx,error):
    errorchan = await bot.fetch_channel(secrets.error_chanid)
    await errorchan.send(f"ERROR\n```\n{error}\n\n {traceback.format_exc()}```")
    



if __name__ == '__main__':
    # When running this file, if it is the 'main' file
    # i.e. its not being imported from another python file run this
    for file in os.listdir("cogs/"):
        if file.endswith(".py") and not file.startswith("_"):
            bot.load_extension(f"cogs.{file[:-3]}")
    bot.run(token=secrets.bot_token)
