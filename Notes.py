# 	Friendly Telegram (telegram userbot)
# 	Copyright (C) 2018-2019 The Authors

# 	This program is free software: you can redistribute it and/or modify
# 	it under the terms of the GNU Affero General Public License as published by
# 	the Free Software Foundation, either version 3 of the License, or
# 	(at your option) any later version.

# 	This program is distributed in the hope that it will be useful,
# 	but WITHOUT ANY WARRANTY; without even the implied warranty of
# 	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# 	GNU Affero General Public License for more details.

# 	You should have received a copy of the GNU Affero General Public License
# 	along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging

from .. import loader, utils

logger = logging.getLogger("friendly-telegram.modules.notes")


@loader.tds
class NotesMod(loader.Module):
    """Stores global notes (aka snips)"""

    strings = {
        "name": "Notes",
        "what_note": "<b>Какую заметку нужно показать?</b>",
        "no_note": "<b>Заметка не найдена</b>",
        "save_what": "<b>А что сохранить?</b>",
        "what_name": "<b>А как будет называться заметка?</b>",
        "saved": "<b>Заметка сохранена как:</b> <code>{}</code>",
        "notes_header": "<b>Сохранённые заметки:</b>\n\n",
        "notes_item": "<b>▷</b> <code>{}</code>",
        "delnote_args": "<b>А какую заметку нужно удалить?</b>",
        "delnote_done": "<b>Заметка удалена!</b>",
        "delnotes_none": "<b>А заметок-то нету...</b>",
        "delnotes_done": "<b>ВСЕ ЗАМЕТКИ УДАЛЕНЫ</b>",
        "notes_none": "<b>А заметок-то нету...</b>",
    }

    async def findnotecmd(self, message):
        """Gets the note specified"""
        args = utils.get_args(message)
        if not args:
            await utils.answer(message, self.strings("what_note", message))
            return
        asset_id = self._db.get("friendly-telegram.modules.notes", "notes", {}).get(
            args[0], None
        )
        logger.debug(asset_id)
        asset = await self._db.fetch_asset(asset_id) if asset_id is not None else None
        if asset is None or not hasattr(asset, "chat") or not hasattr(asset, "id"):
            self.del_note(args[0])
            await utils.answer(message, self.strings("no_note", message))
            return
        link = f"https://t.me/c/{asset.chat.id}/{asset.id}"
        await message.edit(
            f'<b>Заметка</b> "<code>{args[0]}</code>" <a href="{link}">находится здесь.</a>'
        )

    async def notecmd(self, message):
        """Gets the note specified"""
        args = utils.get_args(message)
        if not args:
            await utils.answer(message, self.strings("what_note", message))
            return
        asset_id = self._db.get("friendly-telegram.modules.notes", "notes", {}).get(
            args[0], None
        )
        logger.debug(asset_id)
        asset = await self._db.fetch_asset(asset_id) if asset_id is not None else None
        if asset is None:
            self.del_note(args[0])
            await utils.answer(message, self.strings("no_note", message))
            return
    
        await message.delete()
    
        reply = await message.get_reply_message()
    
        kwargs = {"reply_to": reply.id} if reply else {}
    
        await message.client.send_message(
            message.peer_id,
            asset,
            **kwargs,
        )

    async def savecmd(self, message):
        """Save a new note. Must be used in reply with one parameter (note name)"""
        args = utils.get_args(message)
        if not args:
            await utils.answer(message, self.strings("what_name", message))
            return
        if message.is_reply:
            target = await message.get_reply_message()
        elif len(args) < 2:
            await utils.answer(message, self.strings("save_what", message))
            return
        else:
            message.entities = None
            message.message = args[1]
            target = message
            logger.debug(target.message)
        asset_id = await self._db.store_asset(target)
        self._db.set(
            "friendly-telegram.modules.notes",
            "notes",
            {
                **self._db.get("friendly-telegram.modules.notes", "notes", {}),
                args[0]: asset_id,
            },
        )
        await utils.answer(message, self.strings("saved", message).format(args[0]))

    async def delnotecmd(self, message):
        """Deletes a note, specified by note name"""
        args = utils.get_args(message)
        if not args:
            await utils.answer(message, self.strings("delnote_args", message))
            return
        self.del_note(args[0])
        await utils.answer(message, self.strings("delnote_done", message))

    def del_note(self, note):
        notes = self._db.get("friendly-telegram.modules.notes", "notes", {})
        try:
            del notes[note]
        except KeyError:
            pass
        else:
            self._db.set("friendly-telegram.modules.notes", "notes", notes)

    async def notescmd(self, message):
        """List the saved notes"""
        notes = self._db.get("friendly-telegram.modules.notes", "notes", {})
        if not notes:
            await utils.answer(message, self.strings("notes_none", message))
            return
        await utils.answer(
            message,
            self.strings("notes_header", message)
            + "\n".join(
                self.strings("notes_item", message).format(key)
                for key in notes
            ),
        )

    async def client_ready(self, client, db):
        self._db = db
