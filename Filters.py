# Module author: @ftgmodulesbyfl1yd
# meta developer: @ftgmodulesbyfl1yd
# modify by: @caesar_do_not_touch

from .. import loader, utils

@loader.tds
class FiltersMod(loader.Module):
    """Фильтры\nИзменен пользователем @caesar_do_not_touch."""
    strings = {"name": "Filters"}

    async def client_ready(self, client, db):
        self.db = db

    async def filtercmd(self, message):
        """Добавить фильтр в список."""
        filters = self.db.get("Filters", "filters", {})
        key = utils.get_args_raw(message) # .lower()
        reply = await message.get_reply_message() 
        chatid = str(message.chat_id)

        if not key and not reply:
            return await utils.answer(message, "<b>Нет аргументов и реплая.</b>")

        if chatid not in filters:
            filters.setdefault(chatid, {})

        if key in filters[chatid]:
            return await utils.answer(message, "<b>Такой фильтр уже есть.</b>")

        if reply:
            if key:
                msgid = await self.db.store_asset(reply)
            else:
                return await utils.answer(message, "<b>Нужны аргументы, чтобы сохранить фильтр!</b>")
        else:
            try:
                msgid = (await message.client.send_message(f'friendly-{(await message.client.get_me()).id}-assets', key.split(' / ')[1])).id
                key = key.split(' / ')[0]
            except IndexError:
                return await utils.answer(message, "<b>Нужен второй аргумент (через / )или реплай.</b>")

        filters[chatid].setdefault(key, msgid)
        self.db.set("Filters", "filters", filters)
        await utils.answer(message, f"<b>Фильтр \"{key}\" сохранён!</b>") 


    async def stopcmd(self, message):
        """Удаляет фильтр из списка."""
        filters = self.db.get("Filters", "filters", {})
        args = utils.get_args_raw(message)
        chatid = str(message.chat_id)

        if chatid not in filters:
            return await utils.answer(message, "<b>В этом чате нет фильтров.</b>")

        if not args:
            return await utils.answer(message, "<b>Нет аргументов.</b>")

        if args:
            try:
                filters[chatid].pop(args)
                self.db.set("Filters", "filters", filters)
                await utils.answer(message, f"<b>Фильтр \"{args}\" удалён из чата!</b>")
            except KeyError:
                return await utils.answer(message, f"<b>Фильтра \"{args}\" нет.</b>")
        else:
            return await utils.answer(message, "<b>Нет аргументов.</b>")


    async def stopallcmd(self, message):
        """Удаляет все фильтры из списка чата."""
        filters = self.db.get("Filters", "filters", {})
        chatid = str(message.chat_id)
 
        if chatid not in filters:
            return await utils.answer(message, "<b>В этом чате нет фильтров.</b>")

        filters.pop(chatid)
        self.db.set("Filters", "filters", filters)
        await utils.answer(message, "<b>Всё фильтры были удалены из списка чата!</b>")


    async def filterscmd(self, message):
        """Показывает список фильтров чата."""
        filters = self.db.get("Filters", "filters", {})
        chatid = str(message.chat_id)

        if chatid not in filters:
            return await utils.answer(message, "<b>В этом чате нет фильтров.</b>")

        msg = ""
        for _ in filters[chatid]:
            msg += f"<b>• {_}</b>\n"
        await utils.answer(message, f"<b>Список фильтров в этом чате: {len(filters[chatid])}\n\n{msg}</b>") 


    async def watcher(self, message):
        try:
            filters = self.db.get("Filters", "filters", {})
            chatid = str(message.chat_id)
            m = message.text.lower()
            if chatid not in filters: return

            for _ in filters[chatid]:
                msg = await self.db.fetch_asset(filters[chatid][_])
                def_pref = self.db.get("friendly-telegram.main", "command_prefix")
                pref = '.' if not def_pref else def_pref[0]

                if len(_.split()) == 1:
                    if _.lower() in m.split():
                        await self.exec_comm(msg, message, pref)
                else:
                    if _.lower() in m:
                        await self.exec_comm(msg, message, pref)
        except: pass

    async def exec_comm(self, msg, message, pref):
        try:
            if msg.text[0] == pref:
                smsg = msg.text.split()
                return await self.allmodules.commands[smsg[0][1:]](await message.reply(smsg[0] +  ' '.join(_ for _ in smsg if len(smsg) > 1)))
            else: pass
        except: pass
        await message.reply(msg)
