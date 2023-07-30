import os
import dotenv
from telethon import TelegramClient
from motor.motor_asyncio import AsyncIOMotorClient
from telethon.sessions import StringSession


dotenv.load_dotenv('.env')

api_id = os.environ.get('API_ID')
api_hash = os.environ.get('API_HASH')
bot_token = os.environ.get('BOT_TOKEN')
msg_getter_session = os.environ.get('MESSAGE_GETTER_SESSION')
db_url = os.environ.get('MONGO_DB_URL')
database_channel = int(os.environ.get('DATABASE_CHANNEL'))
bot_username = os.environ.get('BOT_USERNAME')
owner_id = int(os.environ.get('OWNER_ID'))
database_name = os.environ.get('DATABASE_NAME')
collection_name = os.environ.get('COLLECTION_NAME')

msg_getter = TelegramClient(StringSession(msg_getter_session), api_id, api_hash)

bot = TelegramClient(
        'bot', 
        api_id, 
        api_hash, 
    ).start(bot_token=bot_token)

client = AsyncIOMotorClient(db_url)

# client = MongoClient(db_url, tls=True)


# settings_col = Collection(client['ServiceBot'], f"{database_name}_settings")
# fc = settings_col.find_one({"_id": "Forced_Channel"})
# if fc == None:
#     settings_col.insert_one(
#         {
#             "_id": "Forced_Channel",
#             "msg": "Join this channel and try again.\nThank you for your support :)",
#             "channel_id": "-1001493986200",
#             "channel_link": "https://t.me/+tfcb_W0BssNiNjgx"
#         }
#     )

# fr = settings_col.find_one({"_id": "Forced_Ranges"})
# if fr == None:
#     settings_col.insert_one(
#         {
#             "_id": "Forced_Ranges", 
#             "ranges": dict()
#         }
    # )
