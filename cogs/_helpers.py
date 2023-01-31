from urlextract import URLExtract
import base64
from urllib.parse import urlparse
from cogs._size_calc import GoogleDriveSizeCalculate,service 
import cogs._secrets as secrets
import io
import requests
from requests.structures import CaseInsensitiveDict
from prettytable import PrettyTable
import cogs._db_funcs as dbf

import re
from pyppeteer import launch

import json

from easy_pil import Editor, Font, Text
from easy_pil.utils import load_image

import discord


content_channels = {
    "anime" : 000000000000000000,
    "bookscomicsmanga"  : 000000000000000000,
    "collection" : 000000000000000000 ,
    "courses"  : 000000000000000000,
    "games"  : 000000000000000000,
    "movies"  : 000000000000000000,
    "software" : 000000000000000000 ,
    "tv" : 000000000000000000,
    "miscellaneous":000000000000000000,
    "video":000000000000000000

}

def get_key(my_dict,val):
    for key, value in my_dict.items():
        if val == value:
            return key

def find_urls_from_text(text):
    urlextractor = URLExtract()
    urls = urlextractor.find_urls(text)
    return urls

def b64d(s):
    st = s + '=='
    return base64.urlsafe_b64decode(st.encode()).decode()

def get_ordered_links(urls):
    ourls = {"decoded":"","external":[]}

    for url in urls:
        if "links.gamesdrive.net" in url:
            path = urlparse(url).fragment[6:]
            encodedlink = path.split('.')[0]

            decoded = b64d(encodedlink)
            ourls['decoded'] = decoded
        elif "drive.google.com" in url:
            ourls['decoded'] = url
        else:
            ourls['external'].append(url)
    
    return ourls

def get_name_size_from_durl(downloadurl):
    if not "drive.google.com" in downloadurl: return None,None
    try:
        calculator = GoogleDriveSizeCalculate(service)
        file_details = calculator.gdrive_checker(downloadurl)
        return file_details['name'],file_details['bytes']
    except:
        return None,None

def get_username_from_user_id(userid):
    headers =  CaseInsensitiveDict()
    headers["Authorization"] = f"Bot {secrets.bot_token}"
    x = requests.get(f'https://discord.com/api/users/{userid}',headers=headers).json()
    try:
        return x['username']
    except:
        return userid

def get_readable_file_size(size_in_bytes) -> str:
    SIZE_UNITS = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    if size_in_bytes is None:
        return '0B'
    index = 0
    while size_in_bytes >= 1024:
        size_in_bytes /= 1024
        index += 1
    try:
        return f'{round(size_in_bytes, 2)} {SIZE_UNITS[index]}'
    except IndexError:
        return 'File too large'

def customsort(i):
    return i[1]

async def get_descending_table_for_category(category):
    data = await dbf.get_uploader_uploaded_for_category(category)
    x = PrettyTable()
    x.field_names = ["Rank","Uploader","Uploaded Size"]
    x.align["Rank"] = "c"
    x.align["Uploader"] = "c"
    x.align["Uploaded Size"] = "r"
    datalist = [[k,v] for k,v in data.items()]
    datalist.sort(key=customsort,reverse=True)
    for pos,i in enumerate(datalist[:10]):
        if pos == 0: emo = "🥇"
        elif pos == 1 : emo = "🥈"
        elif pos == 2 : emo = "🥉"
        else: emo = "#"+str(pos+1)
        x.add_row([emo,get_username_from_user_id(i[0]),get_readable_file_size(i[1])])

    return x.get_string()

async def get_overall_descending_table():
    """Overall upload stats"""
    overall = await dbf.get_overall_uploader_uploaded()

    x = PrettyTable()
    x.field_names = ["Rank","Uploader","Uploaded Size"]
    x.align["Rank"] = "c"
    x.align["Uploader"] = "c"
    x.align["Uploaded Size"] = "r"
    datalist = [[k,v] for k,v in overall.items()]
    datalist.sort(key=customsort,reverse=True)
    for pos,i in enumerate(datalist[:10]):
        if pos == 0: emo = "🥇"
        elif pos == 1 : emo = "🥈"
        elif pos == 2 : emo = "🥉"
        else: emo = "#"+str(pos+1)
        x.add_row([emo,get_username_from_user_id(i[0]),get_readable_file_size(i[1])])

    return x.get_string()

async def get_contribution_stats_for_user(userid):
    stats,total_links,total_size = await dbf.user_stats(userid)

    desc = ".\n"
    lenofk = len(stats.keys())
    iterator = 0
    for k,v in stats.items():
        desc+=  f"├── 📁 {k}: {v[0]}\n"
        desc += f"│   └── Size: {get_readable_file_size(v[1])}\n"
        iterator+=1
        if not iterator == lenofk:
            desc +=  "│\n"

    desc += f"\n🔗 Links: {total_links}.\n"
    desc += f"💾 Data: {get_readable_file_size(total_size)}"

    return desc 


async def get_hundred_levels(serverid=None):
    if not serverid:serverid = 974279293842628670
    # browser = await launch(headless=True)
    # page = await browser.newPage()
    # await page.goto(f'https://pepemanager.com/levels/{serverid}')
    # x = await page.evaluate('document.scripts.__NEXT_DATA__.text', force_expr=True)
    # data = json.loads(x)
    # await browser.close()
    # return data['props']['pageProps']['levels']
    data = requests.get(f"https://api.pepemanager.com/levels/{serverid}").json()
    return data['levels']

def getRequiredXp(level: int) -> int:
    return 0 if level == 0 else 100 + 50 * (level - 1) ** 2

def parse_color_hex(string:str):
    if "#" in string: return string
    return "#"+string.strip()

async def generate_rank_card(pos,details,mem_id):
    userdata = await dbf.get_level_img(mem_id)
    background = Editor(load_image(userdata['back'])).resize((934,282))
    try:
        profile = Editor(load_image(f"https://cdn.discordapp.com/avatars/{mem_id}/{details['avatar']}.png?size=4096")).resize((190, 190)).circle_image()
    except:
        profile = Editor(load_image("https://cdn.discordapp.com/embed/avatars/0.png")).resize((190, 190)).circle_image()
    fore_rect = Editor(load_image(userdata['fore'])).resize((894,242))
    poppins = Font.poppins(size=32)
    poppinsSmall = Font.poppins(size=17)
    poppinsMed = Font.poppins(size=33)
    poppinsBig = Font.poppins(size=40)

    background.paste(fore_rect, (20, 20))
    background.paste(profile, (50, 50))
    background.ellipse((42, 42), width=206, height=206, outline=parse_color_hex(userdata['prim']), stroke_width=10)
    background.rectangle((260, 195), width=630, height=40, fill="#484b4e", radius=20)
    background.bar(
        (260, 195),
        max_width=630,
        height=42,
        percentage= round(((getRequiredXp(int(details['level'])+1) - int(details['xp']))*100)/(getRequiredXp(int(details['level'])+1) - getRequiredXp(int(details['level'])))),
        fill=parse_color_hex(userdata['prim']),
        radius=20,
    )
    background.text((270, 140), details["tag"].split("#")[0], font=poppins, color=parse_color_hex(userdata['prim']))
    background.text(
        (880, 124),
        f"{details['xp']} XP / {getRequiredXp(int(details['level'])+1)}",
        font=poppinsMed,
        color=parse_color_hex(userdata['quater']),
        align="right",
    )
    background.text((880, 165), f"({getRequiredXp(int(details['level'])+1)-int(details['xp'])} to Next Level)", font=poppinsSmall, color=parse_color_hex(userdata['prim']),align="right")

    rank_level_texts = [
        Text("Rank ", color=parse_color_hex(userdata['second']), font=poppinsBig),
        Text(f"#{pos}", color=parse_color_hex(userdata['terti']), font=poppinsBig),
        Text("  Level ", color=parse_color_hex(userdata['second']), font=poppinsBig),
        Text(f"{details['level']}", color=parse_color_hex(userdata['terti']), font=poppinsBig),
    ]

    background.multi_text((850, 60), texts=rank_level_texts, align="right")


    file = discord.File(fp=background.image_bytes,filename=f"rank_{mem_id}.png")
    return file

def get_all_tiktok_urls_from_msg(msg):
    if 'tiktok' in msg:
        pattern = r"(@[a-zA-z0-9]*|.*)(\/.*\/|trending.?shareId=)([\d]*)"
        url_exp = re.compile(pattern,re.M)
        urls = url_exp.findall(msg)
        ls = []
        for i in urls:
            t = ''.join(i)
            if 'tiktok' in t:
                ls.append(t)
        return ls
    else: return []

def generate_tiktok_embed_and_file(name,discriminator,avatar_url,tiktok_url):
    api="https://developers.tiklydown.me/api/download?url={}"   
    r:dict = requests.get(api.format(tiktok_url)).json()
    _id = r.get('id')
    if not _id or r.get('error'):
        return None,None
    try:
        t_authout_avatar = r.get('author').get('avatar')
    except AttributeError:
        t_authout_avatar = None
    embed = discord.Embed(color=discord.Color.nitro_pink())
    embed.set_author(name=r['author']['name'],url=f"https://www.tiktok.com/@{r['author']['unique_id']}",icon_url=t_authout_avatar)
    embed.description = f"<{tiktok_url}>\n\n**{r['title']}**\n\n▶️ {r['stats']['playCount']} | 💖 {r['stats']['likeCount']} | 🗨️ {r['stats']['commentCount']} | ➡️ {r['stats']['shareCount']} | 💾 {r['stats']['saveCount']}"
    embed.set_footer(icon_url=avatar_url,text=f"Requested by: {name}#{discriminator}")

    video = requests.get(r['video']['noWatermark'])
    f = io.BytesIO(video.content)
    v_file = discord.File(fp=f,filename=f"TikTok.mp4")
    return v_file,embed