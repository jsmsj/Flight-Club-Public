import motor.motor_asyncio
import certifi
# import _secrets as secrets
import cogs._secrets as secrets
import asyncio
import time

# import sqlite3

ca = certifi.where()


client = motor.motor_asyncio.AsyncIOMotorClient(secrets.dburl,tlsCAFile=ca)

db:motor.motor_asyncio.AsyncIOMotorDatabase = client['flightclub']

categories = [
        "anime",
        "bookscomicsmanga" ,
        "collection" ,
        "courses" ,
        "games" ,
        "movies" ,
        "software" ,
        "tv",
        "miscellaneous",
        "video"
]

general_db:motor.motor_asyncio.AsyncIOMotorCollection = db['general_db']
anime_db = db['anime_db']
bookscomicsmanga_db = db['bookscomicsmanga_db']
collection_db = db['collection_db']
courses_db = db['courses_db']
games_db = db['games_db']
movies_db = db['movies_db']
software_db = db['software_db']
tv_db = db['tv_db']
miscellaneous_db = db['miscellaneous_db']
video_db = db['video_db']
level_img_db = db['level_img_db']

# anime(msgid INT PRIMARY KEY, authorid INT, durl TEXT, exturl TEXT, fname TEXT, size INT)
async def insert_into_db(dbname,msgid:int,authorid:int,durl:str,exturl:str,fname:str,size:int):
    doc = {"_id":msgid,"authorid":authorid,"durl":durl,"exturl":exturl,"fname":fname,"size":size}
    try:
        await db[dbname].insert_one(doc)
    except:
        pass

async def update_into_db(dbname,msgid:int,authorid:int,durl:str,exturl:str,fname:str,size:int):
    x = await db[dbname].find_one({"_id":msgid})

    _id = x['_id']
    doc = {"_id":msgid,"authorid":authorid,"durl":durl,"exturl":exturl,"fname":fname,"size":size}
    try:
        await general_db.replace_one({'_id':_id} , doc)
    except:
        pass


async def message_exists(dbname,msgid):
    return True if await db[dbname].find_one({"_id":msgid}) else False

async def insert_anything_into_db(dbname,doc):
    await db[dbname].insert_one(doc)

async def find_last_msg_timestamp(category):
    x = await general_db.find_one({"category":category})
    return x['timestamp']

async def update_general_db(doc):
    
    x = await general_db.find_one({"category":doc['category']})
  
    _id = x['_id']
    await general_db.replace_one({'_id':_id} , doc)
  

async def get_total_size_for_category(category):
    size = 0
    c = db[f"{category}_db"]
    async for x in c.find({},{"size":1}):
        if x['size']:
            size += x['size']
  
    return size

async def get_size_for_all_categories():
    sizedict = {}
    for category in categories:
        sizedict.update({category:await get_total_size_for_category(category)})

    return sizedict

async def get_total_size_of_all_categories():
    size = 0
    for category in categories:
        size+= await get_total_size_for_category(category)
    return size

async def get_uploader_uploaded_for_category(category):
    """{uploader: size} for a category"""
    x = {}
    c = db[f"{category}_db"]
    async for i in c.find({},{"authorid":1}):
        x.update({i['authorid'] : 0})
    async for j in c.find({},{"authorid":1,'size':1}):
        if j['size']:
            x[j['authorid']] += j['size']
    return x

async def get_overall_uploader_uploaded():
    """{uploader: size} for all categories combined"""
    overall={}
    for category in categories:
        c = db[f"{category}_db"]
        async for i in c.find({},{"authorid":1}):
            exists = overall.get(i['authorid'])
            if not exists:
                overall.update({i['authorid'] : 0})
        
        async for j in c.find({},{"authorid":1,'size':1}):
            if j['size']:
                overall[j['authorid']] += j['size']
    return overall

def customsum(data):
        if len(data) == 0:
            return 0
        else:
            s = 0
            for i in data:
                if i['size']:
                    s+=i['size']
        return s

async def user_stats(userid):
    stats = {}
    total_links = 0
    total_size = 0
    for category in categories:

        c = db[f"{category}_db"]
        all_data = []
        async for i in c.find({"authorid":userid}):
            all_data.append(i)
        links_for_c = len(all_data)
        size_for_c = customsum(all_data)
        total_links += links_for_c

        total_size+=size_for_c
        stats.update({category:[links_for_c,size_for_c]})

    return stats,total_links,total_size
    
async def insert_level_img(userid,back,fore,prim,second,terti,quater):
    doc = {"_id":userid,"back":back,"fore":fore,"prim":prim,"second":second,"terti":terti,"quater":quater}
    try:
        await level_img_db.insert_one(doc)
    except:
        pass

async def update_level_img(userid,back,fore,prim,second,terti,quater):
    x = await level_img_db.find_one({"_id":userid})
    _id = x['_id']
    doc = {"_id":userid,"back":back,"fore":fore,"prim":prim,"second":second,"terti":terti,"quater":quater}
    try:
        await level_img_db.replace_one({'_id':_id},doc)
    except:
        pass

async def update_one_thing_level_img(userid,what_to_update,updated):
    x = await level_img_db.find_one({"_id":userid})
    _id = x['_id']
    x[what_to_update] = updated
    doc = {"_id":userid,"back":x["back"],"fore":x["fore"],"prim":x["prim"],"second":x["second"],"terti":x["terti"],"quater":x["quater"]}
    try:
        await level_img_db.replace_one({'_id':_id},doc)
    except:
        pass

async def get_level_img(userid):
    x = await level_img_db.find_one({"_id":userid})
    if not x:
        await insert_level_img(userid,"https://avatars.mds.yandex.net/i?id=91680738f3229948cdebbd82c36a315f-5870018-images-thumbs&n=13&exp=1","https://avatars.mds.yandex.net/i?id=5ae79e7b88d0812f49941eaa01df93f8551cbedb-4146488-images-thumbs&n=13&exp=1","#00fa81","#F91AFF","#1EAAFF","#32E1FF")
        x = await level_img_db.find_one({"_id":userid})
    return x


