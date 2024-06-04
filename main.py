from pyrogram import Client, filters
from pyrogram.errors import UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied, MessageEmpty, ChannelInvalid
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import os
import threading
import time
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

# Flag to stop operations
stop_operation = False

# Download status
def downstatus(statusfile, message):
    while True:
        if os.path.exists(statusfile):
            break

    time.sleep(2)
    while os.path.exists(statusfile):
        with open(statusfile, "r") as downread:
            txt = downread.read()
        try:
            bot.edit_message_text(
                message.chat.id,
                message.message_id,
                f"__Downloaded__ : **{txt}**"
            )
            time.sleep(2)  # Changed sleep time to 2 seconds
        except:
            time.sleep(4)

# Upload status
def upstatus(statusfile, message):
    while True:
        if os.path.exists(statusfile):
            break

    time.sleep(2)
    while os.path.exists(statusfile):
        with open(statusfile, "r") as upread:
            txt = upread.read()
        try:
            bot.edit_message_text(
                message.chat.id,
                message.message_id,
                f"__Uploaded__ : **{txt}**"
            )
            time.sleep(9)
        except:
            time.sleep(4)

# Progress writer
def progress(current, total, message, type):
    speed = current / (time.time() - progress.start_time)
    file_size_mb = total / (1024 * 1024)  # Convert to MB
    downloaded_mb = current / (1024 * 1024)  # Convert to MB
    if speed > 1:
        speed_str = f"{speed:.2f} MB/s"  # Display speed in MB/s
    else:
        speed_str = f"{speed * 1024:.2f} KB/s"  # Convert speed to KB/s if < 1 MB/s
    estimated_time = (total - current) / speed  # Calculate estimated time
    if estimated_time < 60:
        time_str = f"{estimated_time:.2f} seconds"
    elif estimated_time < 3600:
        time_str = f"{estimated_time / 60:.2f} minutes"
    else:
        time_str = f"{estimated_time / 3600:.2f} hours"

    with open(f'{message.message_id}{type}status.txt', "w") as fileup:
        fileup.write(
            f"{downloaded_mb:.1f} MB / {file_size_mb:.1f} MB\n"
            f"Speed: {speed_str}\n"
            f"Estimated time: {time_str}"
        )

# Start command
@bot.on_message(filters.command(["start"]))
def send_start(client: Client, message):
    global stop_operation
    stop_operation = False
    bot.send_message(
        message.chat.id,
        f"**👋 Hi {message.from_user.mention}, I am Save Restricted Bot. I can send you restricted content by its post link.**\n\n{USAGE}",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⁽ ᴛᴄʀᴇᴘ ₎ 🍿", url="https://t.me/tcrep1")]]),
        reply_to_message_id=message.message_id
    )

# Stop command
@bot.on_message(filters.command(["stop"]))
def stop_operation_command(client: Client, message):
    global stop_operation
    stop_operation = True
    bot.send_message(
        message.chat.id,
        "The process has been stopped by pressing /start to start again 💫."
    )

@bot.on_message(filters.text)
def save(client: Client, message):
    global stop_operation

    copied_count = 0
    error_count = 0

    # Joining chats
    if "https://t.me/+" in message.text or "https://t.me/joinchat/" in message.text:
        if acc is None:
            bot.send_message(message.chat.id, f"**String Session is not Set**")
            return

        try:
            try:
                acc.join_chat(message.text)
            except Exception as e:
                bot.send_message(message.chat.id, f"**Error** : __{e}__")
                return
            bot.send_message(message.chat.id, "**Chat Joined**")
        except UserAlreadyParticipant:
            bot.send_message(message.chat.id, "**Chat already Joined**")
        except InviteHashExpired:
            bot.send_message(message.chat.id, "**Invalid Link**")

   # الحصول على الرسالة
    elif "https://t.me/" in message.text:
        datas = message.text.split("/")
        temp = datas[-1].replace("?single", "").split("-")
        fromID = int(temp[0].strip())
        try:
            toID = int(temp[1].strip())
        except:
            toID = fromID

        for msgid in range(fromID, toID + 1):
            if stop_operation:
                bot.send_message(message.chat.id, "The process has been stopped by pressing /start to start again 💫.")
                return

            try:
                if "https://t.me/c/" in message.text:
                    chatid = int("-100" + datas[4])

                    if acc is None:
                        bot.send_message(message.chat.id,f"**String Session is not Set**", reply_to_message_id=message.id)
                        return

                    try:
                        handle_private(message, chatid, msgid)
                    except ChannelInvalid:
                        bot.send_message(
                            message.chat.id,
                            "⚠️ **Mistake: I cannot access the channel. Send the invitation link first. If you do not have an invitation link, contact support. @l_s_I_I.**",
                            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Support ᔆ ᴾ ᴱ ᴱ ᴰ ™𝓼", url="https://t.me/l_s_I_I")]])
                        )
                        return

                    try:
                        bot.copy_message(message.chat.id, msg.chat.id, msgid)
                        copied_count += 1
                    except:
                        if acc is None:
                            bot.send_message(message.chat.id, f"**String Session is not Set**")
                            return
                        try:
                            handle_private(message, username, msgid)
                            copied_count += 1
                        except Exception as e:
                            if isinstance(e, MessageEmpty):
                                error_count += 1
                            else:
                                bot.send_message(message.chat.id, f"**Error** : __{e}__")

                        # Wait time
                        time.sleep(2)
            except MessageEmpty:
                error_count += 1

        # Send final message
        bot.send_message(
            message.chat.id,
            f"**تم نسخ وتحويل الرسائل**",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⁽ ᴛᴄʀᴇᴘ ₎ 🍿", url="https://t.me/tcrep1")]])
        )

# Handle private
def handle_private(message, chatid, msgid):
    msg = acc.get_messages(chatid, msgid)
    msg_type = get_message_type(msg)

    if "Text" == msg_type:
        bot.send_message(message.chat.id, msg.text, entities=msg.entities)
        return

    progress.start_time = time.time()
    smsg = bot.send_message(message.chat.id, '__Downloading__')
    dosta = threading.Thread(target=lambda: downstatus(f'{message.message_id}downstatus.txt', smsg), daemon=True)
    dosta.start()
    file = acc.download_media(msg, progress=progress, progress_args=[message, "down"])
    os.remove(f'{message.message_id}downstatus.txt')

    upsta = threading.Thread(target=lambda: upstatus(f'{message.message_id}upstatus.txt', smsg), daemon=True)
    upsta.start()

    if "Document" == msg_type:
        try:
            thumb = acc.download_media(msg.document.thumbs[0].file_id)
        except:
            thumb = None

        bot.send_document(
            message.chat.id,
            file,
            thumb=thumb,
            caption=msg.caption,
            caption_entities=msg.caption_entities,
            progress=progress,
            progress_args=[message, "up"]
        )
        if thumb is not None:
            os.remove(thumb)

    elif "Video" == msg_type:
        try:
            thumb = acc.download_media(msg.video.thumbs[0].file_id)
        except:
            thumb = None

        bot.send_video(
            message.chat.id,
            file,
            duration=msg.video.duration,
            width=msg.video.width,
            height=msg.video.height,
            thumb=thumb,
            caption=msg.caption,
            caption_entities=msg.caption_entities,
            progress=progress,
            progress_args=[message, "up"]
        )
        if thumb is not None:
            os.remove(thumb)

    elif "Animation" == msg_type:
        bot.send_animation(message.chat.id, file)

    elif "Sticker" == msg_type:
        bot.send_sticker(message.chat.id, file)

    elif "Voice" == msg_type:
        bot.send_voice(
            message.chat.id,
            file,
            caption=msg.caption,
            caption_entities=msg.caption_entities,
            progress=progress,
            progress_args=[message, "up"]
        )

    elif "Audio" == msg_type:
        try:
            thumb = acc.download_media(msg.audio.thumbs[0].file_id)
        except:
            thumb = None

        bot.send_audio(
            message.chat.id,
            file,
            caption=msg.caption,
            caption_entities=msg.caption_entities,
            performer=msg.audio.performer,
            title=msg.audio.title,
            duration=msg.audio.duration,
            thumb=thumb,
            progress=progress,
            progress_args=[message, "up"]
        )
        if thumb is not None:
            os.remove(thumb)

    elif "Photo" == msg_type:
        bot.send_photo(
            message.chat.id,
            file,
            caption=msg.caption,
            caption_entities=msg.caption_entities,
            progress=progress,
            progress_args=[message, "up"]
        )

    os.remove(f'{message.message_id}upstatus.txt')
    bot.delete_messages(message.chat.id, smsg.message_id)
    os.remove(file)

# Get message type
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
