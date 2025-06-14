import io
from .. import loader, utils

@loader.tds
class SavedMod(loader.Module):
    """Соxранятель в избранное"""
    strings = {"name": "SavedMessages", "to": "me"}

    @loader.unrestricted
    async def savedcmd(self, message):
        """.saved реплай на медиа"""
        await message.delete()
        reply = await message.get_reply_message()
        name = utils.get_args_raw(message)

        if not reply or not reply.media:
            return

        is_disappearing = getattr(reply.media, "ttl_seconds", None)
        is_view_once = getattr(reply.media, "view_once", False)

        # Если исчезающее или разовый просмотр — загрузим вручную
        if is_disappearing or is_view_once:
            # Скачиваем медиа как байты
            file = await reply.download_media(bytes)
            file = io.BytesIO(file)
            # Имя файла: либо аргумент, либо auto
            ext = reply.file.ext if reply.file else ".media"
            file.name = name or f"{reply.sender_id}{ext}"
            file.seek(0)
            await message.client.send_file(self.strings["to"], file)
        else:
            # Обычное медиа — просто форвардим
            await reply.forward_to(self.strings["to"])
