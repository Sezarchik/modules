__version__ = (0, 0, 2)

# for more info: https://murix.ru/files/ftg
# by xadjilut, 2021

# модуль частично не мой | This module is not half mine.

# _           _            _ _
# | |         | |          (_) |
# | |     _ | |_ _  _ _| | 
# | |    / _ \| / _ \/ | | |/ /
# | |_| (_) | || (_) \ \ |   <
# \_/\_/ \\_/|_/_|_|\_\
#
#              © Copyright 2022
#
#         developed by @lotosiiik, @byateblan

# meta developer: @hikkaftgmods
# modify by: @caesar_do_not_touch
# meta banner: https://te.legra.ph/file/a428776824470e0bdccb6.jpg
# meta pic: https://te.legra.ph/file/98192f1f7953275baead5.jpg

import random
import re
from .. import loader, utils
from datetime import timedelta, datetime
from telethon import functions
from telethon.tl.types import Message

@loader.tds
class FarmIrisMod(loader.Module):
    """Для автоматического фарминга коинов в ирисботе"""

    strings = {
        "name": "farmiris",
        "farmon": "<i>✅Отложенка создана, автофарминг запущен, всё начнётся через 20 секунд...</i>",
        "farmon_already": "<i>Уже запущено</i>",
        "farmoff": "<i>❌Автофарминг остановлен.\n☢️Надюпано:</i> <b>%coins% i¢</b>",
        "farm": "<i>☢️Надюпано:</i> <b>%coins% i¢</b>",
    }

    def __init__(self):
        self.name = self.strings["name"]

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.myid = (await client.get_me()).id
        self.iris = 5443619563

    async def farmoncmd(self, message):
        """Запустить автофарминг"""
        status = self.db.get(self.name, "status", False)
        if status:
            message = await utils.answer(message, self.strings["farmon_already"])
            return
        self.db.set(self.name, "status", True)
        peer = await self.client.get_input_entity(self.iris)
        await self.client.send_message(
            peer, "Фарма", schedule=datetime.now() + timedelta(seconds=20)
        )
        message = await utils.answer(message, self.strings["farmon"])

    async def farmoffcmd(self, message):
        """Остановить автофарминг"""
        self.db.set(self.name, "status", False)
        coins = self.db.get(self.name, "coins", 0)
        if coins:
            self.db.set(self.name, "coins", 0)
        message = await utils.answer(message, self.strings["farmoff"].replace("%coins%", str(coins)))

    async def farmcmd(self, message):
        """Вывод кол-ва коинов, добытых этим модулем"""
        coins = self.db.get(self.name, "coins", 0)
        message = await utils.answer(message, self.strings["farm"].replace("%coins%", str(coins)))

    async def watcher(self, event):
        if not isinstance(event, Message):
            return
        chat = utils.get_chat_id(event)
        if chat != self.iris:
            return
        status = self.db.get(self.name, "status", False)
        if not status:
            return
        peer = await self.client.get_input_entity(self.iris)

        if event.raw_text == "Фарма":
            return await self.client.send_message(
                peer, "Фарма", schedule=datetime.now() + timedelta(minutes=random.randint(1, 20))
            )

        if event.sender_id != self.iris:
            return

        if "НЕЗАЧЁТ!" in event.raw_text:
            match = re.search(r"через ([^\n]+)", event.raw_text.lower())
            if not match:
                return

            time_str = match.group(1)

            hours = minutes = seconds = 0

            if 'час' in time_str:
                match = re.search(r"(\d+)\s*час", time_str)
                if match:
                    hours = int(match.group(1))
            if 'мин' in time_str:
                match = re.search(r"(\d+)\s*мин", time_str)
                if match:
                    minutes = int(match.group(1))
            if 'сек' in time_str:
                match = re.search(r"(\d+)\s*сек", time_str)
                if match:
                    seconds = int(match.group(1))

            randelta = random.randint(20, 60)
            delta = timedelta(hours=hours, minutes=minutes, seconds=seconds + randelta)

            try:
                sch = (await self.client(functions.messages.GetScheduledHistoryRequest(peer=peer, hash=0))).messages
                if sch:
                    await self.client(
                        functions.messages.DeleteScheduledMessagesRequest(peer=peer, id=[x.id for x in sch])
                    )
            except Exception:
                pass

            schedule_time = datetime.now() + delta
            return await self.client.send_message(peer, "Фарма", schedule=schedule_time)

        if "ЗАЧЁТ" in event.raw_text or "УДАЧА" in event.raw_text:
            args = event.raw_text.split()
            for x in args:
                if x[0] == "+":
                    coins = int(x[1:])
                    total = self.db.get(self.name, "coins", 0) + coins
                    self.db.set(self.name, "coins", total)
                    return

    async def message_q(
        self,
        text: str,
        user_id: int,
        mark_read: bool = False,
        delete: bool = False,
    ):
        """Отправляет сообщение и возращает ответ"""
        async with self.client.conversation(user_id) as conv:
            msg = await conv.send_message(text)
            response = await conv.get_response()
            if mark_read:
                await conv.mark_read()

            if delete:
                await msg.delete()
                await response.delete()

            return response

    @loader.command()
    async def bagcmd(self, message):
        """Показывает ваш мешок"""

        bot = "@iris_black_bot"
        bags = await self.message_q(
            "Мешок",
            bot,
            delete=True,
        )

        args = utils.get_args_raw(message)

        if not args:
            await utils.answer(message, bags.text)
