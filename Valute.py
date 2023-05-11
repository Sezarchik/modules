# Name: Valute
# Description: Конвертер Валют
# Author: Yahikoro
# Commands:
# .val
# modify by: @caesar_do_not_touch
# ---------------------------------------------------------------------------------


import asyncio
from asyncio.exceptions import TimeoutError
from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError

from .. import loader, utils


def register(cb):
    cb(ValuteMod())


class ValuteMod(loader.Module):
    """Конвертер Валют"""

    strings = {"name": "Конвертер Валют"}

    async def valcmd(self, message):
        """.val + количество + валюта"""
        state = utils.get_args_raw(message)
        await utils.answer(message, "<b>Данные получены</b>")
        chat = "@exchange_rates_vsk_bot"
        async with message.client.conversation(chat) as conv:
            try:
                await utils.answer(message, "<b>Конвертирую...</b>")
                response = conv.wait_event(
                    events.NewMessage(incoming=True, from_users=1210425892)
                )
                bot_send_message = await message.client.send_message(
                    chat, format(state)
                )
                bot_response = response = await response
            except YouBlockedUserError:
                await utils.answer(message, "<b>Убери из ЧС:</b> " + chat)
                return
            except TimeoutError:
                await utils.answer(message, "<b>Таймаут, брад.</b>")
                return
            await bot_send_message.delete()
            await utils.answer(message, response.text)
            await bot_response.delete()
