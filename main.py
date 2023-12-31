from telethon import events, Button
from config import bot, bot_username, database_channel, owner_id, approved_users, btntxt, btnlink
from motormongo import UsersDB, SettingsDB, ForceReqDB, AffiliateDB
import asyncio
import json
import logging
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError
from telethon import types
from datetime import datetime

UsersDB = UsersDB()
SettingsDB = SettingsDB()
ForceReqDB = ForceReqDB()
AffiliateDB = AffiliateDB()

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=logging.WARN)


link_format = """
┃█████████████████████
[FILENAME]
┃█████████████████████
JUST CLICK AND PRESS START
"""


@bot.on(events.NewMessage(pattern=btntxt))
async def _(event):
    await event.reply(btnlink)


@bot.on(events.NewMessage(pattern="/broadcast", chats=owner_id))
async def _(event):
    msg = await event.get_reply_message()
    offset = None
    limit = None
    count = 0
    if event.raw_text == "/broadcast":
        users = await UsersDB.full()
    else:
        _, offset, limit = event.raw_text.split()
        if offset == "random":
            users = await UsersDB.rando(sample_size=limit)
        else:
            users = await UsersDB.range(offset=int(offset), limit=int(limit))
    for i in users:
        try:
            await bot.send_message(i['_id'], msg)
            await asyncio.sleep(0.5)
        except Exception as e:
            count += 1
            print(e)
    await event.reply(f"Broadcast Done, Offset={offset}, Limit={limit}, Count={count}")


@bot.on(events.NewMessage(pattern="/start"))
async def _(event):
    dbc = database_channel
    linktype = None
    try:
        source = None
        if "affiliate" in event.raw_text:
            source = event.raw_text.split()[1].split("affiliate")[1]
        
        await UsersDB.add(
            {
                "_id": event.chat_id, 
                "username": event.sender.username, 
                "name": f"{event.sender.first_name} {event.sender.last_name}",
                "uid": int(await UsersDB.count()) + 1,
                "source": source
            }
        )

    except Exception as e:
        print(e)
    
    data = await SettingsDB.find({"_id": "Forced_Channel"})
    range_data = await SettingsDB.find({"_id": "Forced_Ranges"})
    fchannel_id = int(data["channel_id"])
    message = data["msg"]
    flink = data["channel_link"].replace("@", "t.me/")
    try:
        is_req_set = data["is_req_set"]
    except:
        is_req_set = "False"

    if "client" in event.raw_text:
        linktype = "client"

    if "affiliate" in event.raw_text:
        linktype = "affiliate"
        affiliate = event.raw_text.split()[1].split(linktype)[1]
        affiliate_data = dict(await AffiliateDB.find({"_id": affiliate}))
        fchannel_id = int(affiliate_data["channel_id"])
        flink = affiliate_data["channel_link"]
        is_req_set = affiliate_data["is_req_set"]
        message = affiliate_data["msg"]
        dbc = int(affiliate_data["database_channel"])

    else:
        user = await UsersDB.find({"_id":event.chat_id})
        uid = user["uid"]
        ranges = range_data["ranges"]
        for range_key, range_value in ranges.items():
            range_start, range_end = map(int, range_key.split('-'))
            if range_start <= uid <= range_end:
                fchannel_id = range_value["channel_id"]
                flink = range_value["channel_link"]
                is_req_set = range_value["is_req_set"]
                message = range_value["msg"]
                break
        
    try:
        event_text = event.raw_text.replace("-0099", "")
        if "-0099" in event.raw_text:
            pass

        elif is_req_set == "Fake":
            buttons = [
            Button.url("Join Channel Now", flink),
            Button.url("Try again", f"t.me/{bot_username}?start={event.raw_text.split()[1]}-0099")
            ]
            await bot.send_message(event.chat_id, message, buttons=buttons)
            return

        elif is_req_set == "True":
            existing_users = await ForceReqDB.find({'_id': fchannel_id})
            existing_users = set(existing_users['users'])
            if event.chat_id not in existing_users:
                1/0

        else:
            await bot(GetParticipantRequest(channel=fchannel_id, participant=event.sender_id))

        if event.raw_text == "/start":
            await event.reply(
                "This bot is to get links of anime files.",
                buttons=[
                        Button.text(btntxt, resize=True, single_use=True)
                    ]
            )

        else:
            if event_text.split()[1].split('_')[0] == "single":
                try:
                    _, channel_id, msg_id = event_text.split()[1].split(linktype)[0].split('_')
                    
                    file_msg = await bot.get_messages(int(channel_id), ids=int(msg_id))
                    
                    await bot.send_message(
                        event.chat_id,
                        file_msg
                        )

                except Exception as e:
                    print(e)
                    await bot.send_message(event.chat_id, "No file with such id found")
            
            else:
                try:
                    _, start_id, end_id = event_text.split()[1].split(linktype)[0].split('_')
                    start_id, end_id = int(start_id), int(end_id)
                    ids = []
                    for i in range(start_id, end_id + 1):
                        ids.append(i)

                    files_msg = await bot.get_messages(dbc, ids=ids) 
                    for i in files_msg:
                        await bot.send_message(event.chat_id, i)
                        await asyncio.sleep(1)
                except Exception as e:
                    print(e)
                    await bot.send_message(event.chat_id, "No file with such id found")
                    
    except (UserNotParticipantError, ZeroDivisionError):
        buttons = [
            Button.url("Join Channel Now", flink),
        ]
        try:
            buttons.append(Button.url("Try again", f"t.me/{bot_username}?start={event.raw_text.split()[1]}"))
        except:
            pass
        await bot.send_message(event.chat_id, message, buttons=buttons)

    
@bot.on(events.NewMessage(pattern="/set_force", chats=approved_users))
async def _(event):
    msg = await event.get_reply_message()
    if msg == None:
        await event.reply("channel_id|-100xyz\n\nis_req_set|False\n\nchannel_link|t.me/xyz\n\nmsg|Join this channel and try again.\nThank you for your support")
    else:
        data = msg.raw_text.split("\n\n")
        fch = {"_id": "Forced_Channel"}
        for i in data:
            d1 = i.split("|")
            fch[d1[0]] = d1[1]

        await SettingsDB.modify({"_id": "Forced_Channel"}, fch)
        await event.reply(f"Forced Channel Updated \n\n{fch}.\n\n Remember to add me to the channel and make me admin.")


@bot.on(events.NewMessage(pattern="/set_range", chats=approved_users))
async def _(event):
    msg = await event.get_reply_message()
    if msg == None:
        await event.reply("range|1-100\n\nchannel_id|-100xyz\n\nchannel_link|t.me/xyz\n\nis_req_set|False\n\nmsg|Join this channel and try again.\nThank you for your support")
    else:
        data = msg.raw_text.split("\n\n")
        range_data = dict() 
        for i in data:
            d1 = i.split("|")
            range_data[d1[0]] = d1[1]

        new_range = range_data["range"]
        new_range_start, new_range_end = map(int, new_range.split("-"))
        channel_id = int(range_data["channel_id"])
        channel_link = range_data["channel_link"]
        is_req_forced = range_data["is_req_set"]
        message = range_data["msg"]
        existing_ranges = await SettingsDB.find({"_id": "Forced_Ranges"})

        for existing_range in existing_ranges["ranges"].keys():
            existing_start, existing_end = map(int, existing_range.split('-'))
            if (existing_start <= new_range_start <= existing_end) or (existing_start <= new_range_end <= existing_end) or (new_range_start >= existing_start and new_range_end <= existing_end) or (new_range_start <= existing_start and new_range_end >= existing_end): 
                await event.reply(f"Overlap with existing range.\n\n{existing_range}")
                return
        
        existing_ranges["ranges"][new_range] = {
            "channel_link": channel_link, 
            "channel_id": channel_id, 
            "msg": message, 
            "is_req_set": is_req_forced
        }

        await SettingsDB.modify({"_id": "Forced_Ranges"}, existing_ranges)
        if is_req_forced == "True":
            await ForceReqDB.add({"_id": channel_id, "users": []})
        await event.reply(f"New force range set successfully\n\n{existing_ranges['ranges'][new_range]}")


@bot.on(events.NewMessage(pattern="/new_affiliate", chats=approved_users))
async def _(event):
    msg = await event.get_reply_message()
    if msg == None:
        await event.reply("affiliate_id|xyz\n\ndatabase_channel|-100xyz")
    else:
        data = msg.raw_text.split("\n\n")
        aff_data = dict() 
        for i in data:
            d1 = i.split("|")
            aff_data[d1[0]] = d1[1]
    
        aff_id = aff_data["affiliate_id"]
        database_channel = aff_data["database_channel"]
        await AffiliateDB.add({
            "_id": aff_id,
            "database_channel": database_channel
        })
        await event.reply("Affiliate added successfully.")            


@bot.on(events.NewMessage(pattern="/affiliate_set_force", chats=approved_users))
async def _(event):
    msg = await event.get_reply_message()
    if msg == None:
        await event.reply("affiliate_id|xyz\n\ndatabase_channel|-100xyz\n\nchannel_id|-100xyz\n\nchannel_link|t.me/xyz\n\nis_req_forced|False\n\nmsg|Join this channel and try again.\nThank you for your support")
    else:
        data = msg.raw_text.split("\n\n")
        fch = {}
        for i in data:
            d1 = i.split("|")
            fch[d1[0]] = d1[1]

        if fch["is_req_forced"] == "True":
            await ForceReqDB.add({"_id": int(fch["channel_id"]), "users": []})

        await AffiliateDB.modify({"_id": fch["affiliate_id"]}, fch)
        await event.reply(f"Forced Channel Updated \n\n{fch}.\n\n Remember to add me to the channel and make me admin.")


@bot.on(events.NewMessage(pattern="/rm_range", chats=approved_users))
async def _(event):
    rm_range = event.raw_text.split()[1]
    existing_ranges = await SettingsDB.find({"_id": "Forced_Ranges"})
    try:
        existing_ranges['ranges'].pop(rm_range)
        await SettingsDB.modify({"_id": "Forced_Ranges"}, existing_ranges)
        await event.reply("Range deleted successfully.")
    except Exception as e:
        await event.reply(f"Error\n\n{e}")


@bot.on(events.NewMessage(pattern="/stats"))
async def _(event):
    count = await UsersDB.count()
    forced_data = await SettingsDB.find({"_id": "Forced_Channel"})
    ranges_data = await SettingsDB.find({"_id": "Forced_Ranges"})
    ranges_stats = ""
    for k, v in ranges_data["ranges"].items():
        ranges_stats += f"\n{k}: {v['channel_link']}"
    aff_data = await AffiliateDB.full()
    aff_str = ""
    for i in aff_data:
        aff_count = await UsersDB.count({"source": str(i["_id"])})
        aff_str += f"{i['_id']}:{aff_count}\n"
    await event.reply(f"Statistics for bot:\n Total number of users: {count}\n\n Default Forced Channel: {forced_data['channel_link']}\n\nRanged Forced Channels: {ranges_stats}", link_preview=False)
    await event.reply(f"Affiliate contribution:\n\n{aff_str}")
    if "export" in event.raw_text:
        await event.reply("Uploading file please wait...")
        userdata = await UsersDB.full()
        with open("userdata.json", "w") as final:
            json.dump(userdata, final, indent=4)
        await event.reply(f"Statistics for bot:\n Total number of users: {count}\n\n Default Forced Channel: {forced_data['channel_link']}\n\n Ranged Forced Channels: {ranges_stats}", file="userdata.json")


@bot.on(events.NewMessage(func=lambda e: e.is_private, incoming=True))
async def _(event):
    aff = await AffiliateDB.full()
    aff_list = []
    for i in aff:
        aff_list.append(i["_id"])
    if event.file:
        if str(event.chat_id) in aff_list:
            await event.reply(f"[{event.file.name}](t.me/{bot_username}?start=single_{event.chat_id}_{event.id}affiliate{event.chat_id})")
        if event.chat_id == owner_id:
            await event.reply(f"Owner link: [{event.file.name}](t.me/{bot_username}?start=single_{event.chat_id}_{event.id})")


@bot.on(events.NewMessage(pattern="/create_link"))
async def _(event):
    data = event.raw_text.split(" ", 1)
    file_range = data[1].strip().replace("-", "_")    
    await event.reply(f"t.me/{bot_username}?start=batch_{file_range}")


@bot.on(events.Raw(types.UpdateBotChatInviteRequester))
async def _(event):
    channel_id = await bot.get_peer_id(event.peer, add_mark=True)
    user_id = event.user_id
    
    await ForceReqDB.modify(
        {"_id": channel_id},
        {"$addToSet": {"users": user_id}}
    )


bot.start()

bot.run_until_disconnected()
