from aiogram import Router, types
from aiogram.filters import Command
from utils.downloader import search_music
from utils.uploader import send_audio

router = Router()


@router.message(Command("music"))
async def music_intro(message: types.Message):
    await message.answer("🎵 Musiqa nomini yozing (masalan: Shoxrux - Yig'lama)")


@router.message()
async def music_search(message: types.Message):
    query = message.text.strip()
    if not query:
        return

    await message.answer("🔍 Musiqa qidirilmoqda...")
    try:
        url, title = search_music(query)
        await send_audio(message, url, title)
    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}")
