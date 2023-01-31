"""Imports"""
import discord
from discord.ext import commands,tasks
import cogs._db_funcs as dbf
import cogs._helpers as hp
import asyncio
from datetime import datetime
import cogs._secrets as secrets
import pytz



class StatisticsEvents(commands.Cog):
    """StatisticsEvents commands"""

    def __init__(self, bot):
        self.bot:commands.Bot = bot
        self.size_update_voice_channel.start()

    async def cog_before_invoke(self, ctx):
        """
        Triggers typing indicator on Discord before every command.
        """
        await ctx.trigger_typing()    
        return

    @tasks.loop(hours=2)
    async def size_update_voice_channel(self):
        await self.update_total_size_on_server()
        print('updated size on server')

    @size_update_voice_channel.before_loop
    async def before_size_update_voice_channel(self):
        print('waiting for bot to be ready')
        await self.bot.wait_until_ready()

    async def insert_msg_in_db(self,message:discord.Message,type="original"):
        
        msgid = message.id
        dbname = hp.get_key(hp.content_channels,message.channel.id)
        if type=="original":
            if not await dbf.message_exists(dbname,msgid):
                authorid = message.author.id
                msgcontent = message.content
                urls_dict = hp.get_ordered_links(hp.find_urls_from_text(msgcontent))
                durl = urls_dict['decoded']
                try:
                    msgembed:discord.Embed = message.embeds[0]
                    emburl = msgembed.url
                except:
                    emburl = None
                    
                if emburl:
                    exturl = emburl
                else:
                    exturl = ' | '.join(urls_dict['external'])
                
                if not durl : return
                fname,size = hp.get_name_size_from_durl(durl)
                print(f'inserting {message.id}')
                await dbf.insert_into_db(dbname+"_db",msgid,authorid,durl,exturl,fname,size)
                print(f'inserted {message.id}')
                await dbf.update_general_db({"category":dbname,"timestamp":message.created_at.timestamp()})
                print('updated generaldb')
                await message.add_reaction("✅")
        if type == "edited":
            authorid = message.author.id
            msgcontent = message.content
            urls_dict = hp.get_ordered_links(hp.find_urls_from_text(msgcontent))
            durl = urls_dict['decoded']
            try:
                msgembed:discord.Embed = message.embeds[0]
                emburl = msgembed.url
            except:
                emburl = None
                
            if emburl:
                exturl = emburl
            else:
                exturl = ' | '.join(urls_dict['external'])
            
            if not durl : return
            fname,size = hp.get_name_size_from_durl(durl)
            print(f'updating {message.id}')
            await dbf.update_into_db(dbname+"_db",msgid,authorid,durl,exturl,fname,size)
            print(f'updated {message.id}')

    async def update_total_size_on_server(self):
        channel = self.bot.get_channel(secrets.total_size_channel_id)
        new_name = f"Total Size: {hp.get_readable_file_size(await dbf.get_total_size_of_all_categories())}"
        await channel.edit(name=new_name)


    async def update_messages_to_db(self,chname,chid,last_saved_timestamp):
        channel = self.bot.get_channel(chid)
        to_add = await channel.history(after=datetime.fromtimestamp(last_saved_timestamp,tz=pytz.UTC)).flatten()
        for msg in to_add: 
            await self.insert_msg_in_db(msg,type="original")
        if len(to_add)!=0:
            dbname = hp.get_key(hp.content_channels,to_add[-1].channel.id)
            await dbf.update_general_db({"category":dbname,"timestamp":to_add[-1].created_at.timestamp()})
    

    @commands.Cog.listener()
    async def on_ready(self):
        last_messages = {k:await dbf.find_last_msg_timestamp(k) for k in hp.content_channels.keys()}
        to_update = []
        for chname,chid in hp.content_channels.items():
            channel = self.bot.get_channel(chid)
            last_msg = await channel.history(limit=1).flatten()
            if int(last_msg[0].created_at.timestamp()) != int(last_messages[chname]):
                to_update.append([chname,chid,last_messages[chname]])
        print(to_update)
        for i in to_update:
            await self.update_messages_to_db(*i)

        if len(to_update)!=0:
            print('Updated those messages which were sent when bot was down.')
        else:
            print('no messages to update')      

    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):
        if message.author.bot : return
        if message.channel.id in hp.content_channels.values():
            await self.insert_msg_in_db(message,type="original")
    
    @commands.Cog.listener()
    async def on_message_edit(self, before_message, after_message:discord.Message):
        if after_message.author.bot : return
        if after_message.channel.id in hp.content_channels.values():
            await self.insert_msg_in_db(after_message,type="edited")  



def setup(bot):
    bot.add_cog(StatisticsEvents(bot))
    print("StatisticsEvents cog is loaded")