# ---------------------------------------------------------------------------------
#  /\_/\  🌐 This module was loaded through https://t.me/hikkamods_bot
# ( o.o )  🔓 Not licensed.
#  > ^ <   ⚠️ Owner of heta.hikariatama.ru doesn't take any responsibilities or intellectual property rights regarding this script
# ---------------------------------------------------------------------------------
# Name: Circles
# Description: Округляет всё
# Author: KeyZenD
# Commands:
# .round
# Edited by @Caesar_GRENKA
# ---------------------------------------------------------------------------------


import io
import logging
import os

from moviepy.editor import VideoFileClip
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from telethon.tl.types import DocumentAttributeFilename

from .. import loader, utils  # pylint: disable=relative-beyond-top-level

logger = logging.getLogger(__name__)


def register(cb):
    cb(CirclesMod())


@loader.tds
class CirclesMod(loader.Module):
    """округляет всё"""

    strings = {"name": "Circles"}

    def __init__(self):
        self.name = self.strings["name"]

    async def client_ready(self, client, db):
        self.client = client

    @loader.sudo
    async def roundcmd(self, message):
        """.round <Reply to image/sticker or video/gif>"""
        reply = None
        if message.is_reply:
            reply = await message.get_reply_message()
            data = await check_media(reply)
            if isinstance(data, bool):
                await utils.answer(
                    message, "<b>Reply to image/sticker or video/gif!</b>"
                )
                return
        else:
            await utils.answer(message, "<b>Reply to image/sticker or video/gif!</b>")
            return
        data, type = data
        if type == "img":
            await message.edit("<b>Processing image</b>📷")
            img = io.BytesIO()
            bytes = await message.client.download_file(data, img)
            im = Image.open(img)
            w, h = im.size
            img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            img.paste(im, (0, 0))
            m = min(w, h)
            img = img.crop(((w - m) // 2, (h - m) // 2, (w + m) // 2, (h + m) // 2))
            w, h = img.size
            mask = Image.new("L", (w, h), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((10, 10, w - 10, h - 10), fill=255)
            mask = mask.filter(ImageFilter.GaussianBlur(2))
            img = ImageOps.fit(img, (w, h))
            img.putalpha(mask)
            im = io.BytesIO()
            im.name = "img.webp"
            img.save(im)
            im.seek(0)
            await message.client.send_file(message.to_id, im, reply_to=reply)
        else:
            await message.edit("<b>Processing GIF/video → circle</b>🎥")
            
            input_file = "input_temp.mp4"
            output_file = "circle_output.mp4"
            
            try:
                # Скачиваем оригинал
                await message.client.download_media(reply, input_file)
                
                # ffmpeg: crop to square + pad to even size + force compatible encoding
                # -vf "crop=min(iw,ih):min(iw,ih),scale=640:640:force_original_aspect_ratio=decrease,pad=640:640:(ow-iw)/2:(oh-ih)/2"
                # + лимит 60 сек, fps 30, yuv420p (Telegram требует для video_note)
                
                cmd = [
                    "ffmpeg", "-y", "-i", input_file,
                    "-vf", "crop=min(iw\\,ih):min(iw\\,ih),scale=640:640:force_original_aspect_ratio=decrease,pad=640:640:(ow-iw)/2:(oh-ih)/2",
                    "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                    "-r", "30", "-t", "60",
                    output_file
                ]
                
                import subprocess
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    error_msg = result.stderr or "Unknown ffmpeg error"
                    await utils.answer(message, f"<b>ffmpeg failed:</b>\n<code>{error_msg[:500]}</code>")
                    return
                
                # Отправляем как video_note
                await message.client.send_file(
                    message.to_id,
                    output_file,
                    video_note=True,
                    duration=0,  # Telegram сам посчитает
                    reply_to=reply.msg_id if hasattr(reply, 'msg_id') else reply.id
                )
            
            except Exception as e:
                await utils.answer(message, f"<b>Error during processing:</b>\n<code>{type(e).__name__}: {str(e)}</code>")
            
            finally:
                for f in [input_file, output_file]:
                    if os.path.exists(f):
                        try:
                            os.remove(f)
                        except:
                            pass
            
            await message.delete()


async def check_media(reply):
    type = "img"
    if reply and reply.media:
        if reply.photo:
            data = reply.photo
        elif reply.document:
            if (
                DocumentAttributeFilename(file_name="AnimatedSticker.tgs")
                in reply.media.document.attributes
            ):
                return False
            if reply.gif or reply.video:
                type = "vid"
            if reply.audio or reply.voice:
                return False
            data = reply.media.document
        else:
            return False
    else:
        return False
    if not data or data is None:
        return False
    else:
        return (data, type)
