from .. import loader, utils
from telethon import TelegramClient
from telethon.tl.patched import Message
from telethon.tl.types import ChatBannedRights
from telethon.tl.functions.channels import EditBannedRequest


@loader.tds
class AutoBanMod(loader.Module):
    """АвтоБан.\nИзменен пользователем @caesar_do_not_touch."""
    strings = {'name': 'AutoBan'}

    async def client_ready(self, client: TelegramClient, db):
        self.client = client
        self.db = db

    async def abancmd(self, message: Message):
        """Добавить/исключить юзера из автобана.\nИспользуй: .aban <@ или реплай> или <list>."""
        users = self.db.get("AutoBan", "users", [])
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()

        if not (args or reply):
            message = await utils.answer(message, "Нет аргументов или реплая")
            return
        if args == "list":
            if not users:
                message = await utils.answer(message, "Список пуст")
                return
            msg = ""
            for _ in users:
                try:
                    user = await self.client.get_entity(_)
                    msg += f"• <a href=\"tg://user?id={user.id}\">{user.first_name}</a>\n"
                except:
                    users.remove(_)
                    self.db.set("AutoBan", "users", users)
                    message = await utils.answer(message, "Произошла ошибка. Повтори команду")
                    return
            message = await utils.answer(message, f"Список пользователей в автобане:\n\n{msg}")
            return
        try:
            user = await self.client.get_entity(reply.sender_id if reply else args if not args.isnumeric() else int(args))
        except ValueError:
            message = await utils.answer(message, "Не удалось найти пользователя")
            return
        if user.id not in users:
            users.append(user.id)
            text = "добавлен в список"
        else:
            users.remove(user.id)
            text = "удален из списка"

        self.db.set("AutoBan", "users", users)
        message = await utils.answer(message, f"{user.first_name} был {text} автобана")


    async def achatcmd(self, message: Message):
        """Добавить чат в список для автобана.\nИспользуй: .achat."""
        chats = self.db.get("AutoBan", "chats", [])
        args = utils.get_args_raw(message)
        chat_id = message.chat_id

        if args == "list":
            if not chats:
                message = await utils.answer(message, "Список пуст")
                return
            msg = ""
            for _ in chats:
                try:
                    chat = await self.client.get_entity(_)
                    msg += f"• {chat.title} | {chat.id}\n"
                except:
                    chats.remove(_)
                    self.db.set("AutoBan", "users", chats)
                    message = await utils.answer(message, "Произошла ошибка. Повтори команду")
                    return
            message = await utils.answer(message, f"Список чатов для автобана:\n\n{msg}")
            return
        if message.is_private:
            message = await utils.answer(message, "Это не чат!")
            return
        if chat_id not in chats:
            chats.append(chat_id)
            text = "добавлен в список"
        else:
            chats.remove(chat_id)
            text = "удален из списка"

        self.db.set("AutoBan", "chats", chats)
        message = await utils.answer(message, f"Этот чат был {text} чатов для автобана")
        return

    async def watcher(self, message: Message):
        try:
            users = self.db.get("AutoBan", "users", [])
            chats = self.db.get("AutoBan", "chats", [])
            user = message.sender
            chat_id = message.chat_id

            if chat_id not in chats:
                return

            if user.id in users:
                for _ in chats:
                    try:
                        await self.client(
                            EditBannedRequest(
                                _, user.id, ChatBannedRights(
                                    until_date=None, view_messages=True
                                )
                            )
                        )
                    except: pass
                await message.respond(f"{user.first_name} был забанен, потому что находился в списке автобана")
                return
        except:
            pass
