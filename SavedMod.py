import io
from .. import loader, utils

@loader.tds
class SavedMod(loader.Module):
    """Соxраняет исчезающие и одноразовые медиа в Избранное"""
    strings = {"name": "SavedMessages", "to": "me"}

    @loader.unrestricted
    async def savedcmd(self, message):
        """.saved реплай на медиа (в т.ч. одноразовое)"""
        await message.delete()
        reply = await message.get_reply_message()
        name = utils.get_args_raw(message)

        if not reply or not reply.media:
            return

        # Попытка получить содержимое
        try:
            # Даже если file=None — скачиваем
            file_bytes = await reply.download_media(bytes)
            if not file_bytes:
                await message.respond("⚠️ Не удалось скачать медиа.")
                return

            file = io.BytesIO(file_bytes)

            # Определим расширение
            ext = ".media"
            if reply.file and reply.file.ext:
                ext = reply.file.ext
            elif reply.document:
                ext = "." + reply.document.mime_type.split("/")[-1]

            file.name = name or f"{reply.sender_id}{ext}"
            file.seek(0)

            await message.client.send_file(self.strings["to"], file)
        except Exception as e:
            await message.respond(f"❌ Ошибка при сохранении: {e}")
