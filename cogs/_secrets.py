import os
from dotenv import load_dotenv
load_dotenv()

bot_token = os.getenv('bot_token')
prefix = os.getenv('prefix')
sa_email = os.getenv('sa_email')
private_key = os.getenv('private_key')

dburl = os.getenv('dburl')

error_chanid = os.getenv('error_chan_id')

total_size_channel_id = os.getenv('total_size_chan_id')