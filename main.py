from pyrogram import Client, filters
from pyrogram.errors import UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied, RPCError
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import time
import os
import threading
from os import environ

bot_token = environ.get("TOKEN", "")
api_hash = environ.get("HASH", "")
api_id = environ.get("ID", "")
bot = Client("mybot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

ss = environ.get("STRING", "")
if ss is not None:
    acc = Client("myacc", api_id=api_id, api_hash=api_hash, session_string=ss)
    acc.start()
else:
    acc = None

user_sessions = {}

# download status
def downstatus(statusfile, message):
    while True:
        if os.path.exists(statusfile):
            break

    time.sleep(3)
    while os.path.exists(statusfile):
        with open(statusfile, "r") as downread:
            txt = downread.read()
        try:
            bot.edit_message_text(message.chat.id, message.id, f"__Downloaded__ : **{txt}**")
            time.sleep(10)
        except:
            time.sleep(5)

# upload status
def upstatus(statusfile, message):
    while True:
        if os.path.exists(statusfile):
            break

    time.sleep(3)
    while os.path.exists(statusfile):
        with open(statusfile, "r") as upread:
            txt = upread.read()
        try:
            bot.edit_message_text(message.chat.id, message.id, f"__Uploaded__ : **{txt}**")
            time.sleep(10)
        except:
            time.sleep(5)

# progress writter
def progress(current, total, message, type):
    with open(f'{message.id}{type}status.txt', "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")

# start command
@bot.on_message(filters.command(["start"]))
def send_start(client: Client, message):
    bot.send_message(message.chat.id, f"**__👋 Hi** **{message.from_user.mention}**, **I am Save Restricted Bot, I can send you restricted content by its post link__**\n\n{USAGE}",
    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Channel ⁽ ᴛᴄʀᴇᴘ ₎ 🍿 ", url="https://t.me/tcrep1")]]), reply_to_message_id=message.id)

# login command
@bot.on_message(filters.command(["login"]))
def login(client: Client, message):
    bot.send_message(message.chat.id, "Please send your Pyrogram session string. You can get it from @ASBB7bot or @PyrogramTexBot.")

@bot.on_message(filters.text & filters.reply)
def save_session(client: Client, message):
    if message.reply_to_message and message.reply_to_message.text == "Please send your Pyrogram session string. You can get it from @ASBB7bot or @PyrogramTexBot.":
        user_sessions[message.from_user.id] = message.text
        bot.send_message(message.chat.id, "Session saved successfully!")

@bot.on_message(filters.text & ~filters.reply)
def save(client: Client, message):
    print(message.text)

    # joining chats
    if "https://t.me/+" in message.text or "https://t.me/joinchat/" in message.text:
        user_session = user_sessions.get(message.from_user.id, None)
        user_acc = acc if user_session is None else Client("useracc", api_id=api_id, api_hash=api_hash, session_string=user_session)
        if user_session:
            user_acc.start()

        if user_acc is None:
            bot.send_message(message.chat.id, "**String Session is not Set**")
            return

        try:
            try:
                user_acc.join_chat(message.text)
            except Exception as e:
                bot.send_message(message.chat.id, f"**Error** : __{e}__")
                return
            bot.send_message(message.chat.id, "**Chat Joined**")
        except UserAlreadyParticipant:
            bot.send_message(message.chat.id, "**Chat already Joined**")
        except InviteHashExpired:
            bot.send_message(message.chat.id, "**Invalid Link**")

        if user_session:
            user_acc.stop()


    # getting message
    elif "https://t.me/" in message.text:
        datas = message.text.split("/")
        temp = datas[-1].replace("?single", "").split("-")
        fromID = int(temp[0].strip())
        try:
            toID = int(temp[1].strip())
        except:
            toID = fromID

        deleted_messages = 0

        for msgid in range(fromID, toID + 1):
            try:
                # private
                if "https://t.me/c/" in message.text:
                    chatid = int("-100" + datas[4])

                    user_session = user_sessions.get(message.from_user.id, None)
                    user_acc = acc if user_session is None else Client("useracc", api_id=api_id, api_hash=api_hash, session_string=user_session)
                    if user_session:
                        user_acc.start()

                    if user_acc is None:
                        bot.send_message(message.chat.id, "**String Session is not Set**")
                        return

                    handle_private(message, chatid, msgid, user_acc)

                    if user_session:
                        user_acc.stop()

                # bot
                elif "https://t.me/b/" in message.text:
                    username = datas[4]

                    user_session = user_sessions.get(message.from_user.id, None)
                    user_acc = acc if user_session is None else Client("useracc", api_id=api_id, api_hash=api_hash, session_string=user_session)
                    if user_session:
                        user_acc.start()

                    if user_acc is None:
                        bot.send_message(message.chat.id, "**String Session is not Set**")
                        return

                    try:
                        handle_private(message, username, msgid, user_acc)
                    except Exception as e:
                        bot.send_message(message.chat.id, f"**Error** : __{e}__")

                    if user_session:
                        user_acc.stop()

                # public
                else:
                    username = datas[3]

                    try:
                        msg = bot.get_messages(username, msgid)
                    except UsernameNotOccupied:
                        bot.send_message(message.chat.id, f"**The username is not occupied by anyone**")
                        return

                    if msg and msg.chat and msg.id:
                        try:
                            bot.copy_message(message.chat.id, msg.chat.id, msg.id)
                        except RPCError:
                            deleted_messages += 1
                            continue
                    else:
                        deleted_messages += 1
                        continue

                time.sleep(3)

            except RPCError:
                deleted_messages += 1
                continue

        bot.send_message(
            message.chat.id,
            f"**Finished copying messages**\n\n**Deleted messages:** {deleted_messages}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⁽ ᴛᴄʀᴇᴘ ₎ 🍿", url="https://t.me/tcrep1")]])
        )

def handle_private(message, chatid, msgid, user_acc):
    msg = user_acc.get_messages(chatid, msgid)
    if not msg or not msg.chat or not msg.id:
        return

    msg_type = get_message_type(msg)

    if "Text" == msg_type:
        bot.send_message(message.chat.id, msg.text, entities=msg.entities)
        return

    smsg = bot.send_message(message.chat.id, '__Downloading__')
    dosta = threading.Thread(target=lambda: downstatus(f'{message.id}downstatus.txt', smsg), daemon=True)
    dosta.start()
    file = user_acc.download_media(msg, progress=progress, progress_args=[message, "down"])
    os.remove(f'{message.id}downstatus.txt')

    upsta = threading.Thread(target=lambda: upstatus(f'{message.id}upstatus.txt', smsg), daemon=True)
    upsta.start()


    if "Document" == msg_type:
        try:
            thumb = user_acc.download_media(msg.document.thumbs[0].file_id)
        except:
            thumb = None

        bot.send_document(message.chat.id, file, thumb=thumb, caption=msg.caption, caption_entities=msg.caption_entities, progress=progress, progress_args=[message, "up"])
        if thumb is not None:
            os.remove(thumb)

    elif "Video" == msg_type:
        try:
            thumb = user_acc.download_media(msg.video.thumbs[0].file_id)
        except:
            thumb = None

        bot.send_video(message.chat.id, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=thumb, caption=msg.caption, caption_entities=msg.caption_entities, progress=progress, progress_args=[message, "up"])
        if thumb is not None:
            os.remove(thumb)

    elif "Animation" == msg_type:
        bot.send_animation(message.chat.id, file)

    elif "Sticker" == msg_type:
        bot.send_sticker(message.chat.id, file)

    elif "Voice" == msg_type:
        bot.send_voice(message.chat.id, file, caption=msg.caption, caption_entities=msg.caption_entities, progress=progress, progress_args=[message, "up"])

    elif "Audio" == msg_type:
        try:
            thumb = user_acc.download_media(msg.audio.thumbs[0].file_id)
        except:
            thumb = None

        bot.send_audio(message.chat.id, file, caption=msg.caption, caption_entities=msg.caption_entities, progress=progress, progress_args=[message, "up"])
        if thumb is not None:
            os.remove(thumb)

    elif "Photo" == msg_type:
        bot.send_photo(message.chat.id, file, caption=msg.caption, caption_entities=msg.caption_entities)

    os.remove(file)
    if os.path.exists(f'{message.id}upstatus.txt'):
        os.remove(f'{message.id}upstatus.txt')
    bot.delete_messages(message.chat.id, [smsg.id])

def get_message_type(msg):
    try:
        msg.document.file_id
        return "Document"
    except:
        pass

    try:
        msg.video.file_id
        return "Video"
    except:
        pass

    try:
        msg.animation.file_id
        return "Animation"
    except:
        pass

    try:
        msg.sticker.file_id
        return "Sticker"
    except:
        pass

    try:
        msg.voice.file_id
        return "Voice"
    except:
        pass

    try:
        msg.audio.file_id
        return "Audio"
    except:
        pass

    try:
        msg.photo.file_id
        return "Photo"
    except:
        pass

    try:
        msg.text
        return "Text"
    except:
        pass

USAGE = """**FOR PUBLIC CHATS**

**__just send post/s link__**

**FOR PRIVATE CHATS**

**__first send invite link of the chat (unnecessary if the account of string session already member of the chat) then send post/s link__**


**MULTI POSTS**

**__send public/private posts link as explained above with format "from - to" to send multiple messages like below__**

```
https://t.me/xxxx/1001-1010

https://t.me/c/xxxx/101 - 120
```
**__note that space in between doesn't matter__**
"""

# infinity polling
bot.run()
