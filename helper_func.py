# (©)Codexbotz
# Recode by @mrismanaziz
# t.me/SharingUserbot & t.me/Lunatic0de

import asyncio
import base64
import re

from pyrogram import Client, filters, types
from pyrogram.errors import FloodWait, UserNotParticipant

from config import ADMINS, FORCE_SUB_CHANNEL, FORCE_SUB_GROUP


async def subschannel(filter, c: Client, m: types.Message):
    if not FORCE_SUB_CHANNEL:
        return True
    user_id = m.from_user.id
    if user_id in ADMINS:
        return True
    try:
        member = await c.get_chat_member(
            chat_id=FORCE_SUB_CHANNEL, user_id=user_id
        )
    except UserNotParticipant:
        return False

    return member.status in ["creator", "administrator", "member"]


async def subsgroup(filter, c: Client, m: types.Message):
    if not FORCE_SUB_GROUP:
        return True
    user_id = m.from_user.id
    if user_id in ADMINS:
        return True
    try:
        member = await c.get_chat_member(chat_id=FORCE_SUB_GROUP, user_id=user_id)
    except UserNotParticipant:
        return False

    return member.status in ["creator", "administrator", "member"]


async def is_subscribed(filter, c: Client, m: types.Message):
    if not FORCE_SUB_CHANNEL:
        return True
    if not FORCE_SUB_GROUP:
        return True
    user_id = m.from_user.id
    if user_id in ADMINS:
        return True
    try:
        member = await c.get_chat_member(chat_id=FORCE_SUB_GROUP, user_id=user_id)
    except UserNotParticipant:
        return False
    try:
        member = await c.get_chat_member(
            chat_id=FORCE_SUB_CHANNEL, user_id=user_id
        )
    except UserNotParticipant:
        return False

    return member.status in ["creator", "administrator", "member"]


async def encode(string):
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    base64_string = (base64_bytes.decode("ascii")).strip("=")
    return base64_string

async def decode(base64_string):
    base64_string = base64_string.strip("=") # links generated before this commit will be having = sign, hence striping them to handle padding errors.
    base64_bytes = (base64_string + "=" * (-len(base64_string) % 4)).encode("ascii")
    string_bytes = base64.urlsafe_b64decode(base64_bytes) 
    string = string_bytes.decode("ascii")
    return string


async def get_messages(c: Client, message_ids):
    messages = []
    total_messages = 0
    while total_messages != len(message_ids):
        temb_ids = message_ids[total_messages : total_messages + 200]
        try:
            msgs = await c.get_messages(
                chat_id=c.db_channel.id, message_ids=temb_ids
            )
        except FloodWait as e:
            await asyncio.sleep(e.value)
            msgs = await c.get_messages(
                chat_id=c.db_channel.id, message_ids=temb_ids
            )
        except Exception:
            pass
        total_messages += len(temb_ids)
        messages.extend(msgs)
    return messages


async def get_message_id(c: Client, m: types.Message):
    if (
        m.forward_from_chat
        and m.forward_from_chat.id == c.db_channel.id
    ):
        return m.forward_from_message_id
    elif m.forward_from_chat or m.forward_sender_name or not m.text:
        return 0
    else:
        pattern = "https://t.me/(?:c/)?(.*)/(\\d+)"
        matches = re.match(pattern, m.text)
        if not matches:
            return 0
        channel_id = matches.group(1)
        msg_id = int(matches.group(2))
        if channel_id.isdigit():
            if f"-100{channel_id}" == str(c.db_channel.id):
                return msg_id
        elif channel_id == c.db_channel.username:
            return msg_id


subsgc = filters.create(subsgroup)
subsch = filters.create(subschannel)
subsall = filters.create(is_subscribed)
