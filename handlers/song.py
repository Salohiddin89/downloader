import os
from aiogram import Router, types
from aiogram.filters import Command
from utils.music_detect import identify_music_with_pyzam
from utils.downloader import search_music

router = Router()


@router.message(Command("qoshiq"))
async def ask_input(message: types.Message):
    await message.answer(
        "🎧 Qoshiqni aniqlash uchun audio yuboring yoki nomini yozing."
    )


@router.message(lambda msg: msg.audio or msg.voice)
async def detect_from_audio(message: types.Message):
    file = message.audio or message.voice
    file_path = await message.bot.download(file)

    try:
        result = await identify_music_with_pyzam(file_path.name)
    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}")
        result = None

    file_path.close()
    if os.path.exists(file_path.name):
        os.remove(file_path.name)

    if result:
        await message.answer(
            f"🎧 Topilgan musiqa:\n"
            f"🎵 {result['title']} - {result['subtitle']}\n"
            f"🔗 {result['url']}"
        )
    else:
        await message.answer("❌ Musiqa aniqlanmadi.")
    

@router.message(lambda msg: msg.text)
async def detect_from_text(message: types.Message):
    query = message.text.strip()
    if not query:
        return
    url, title = search_music(query)
    await message.answer(f"🔍 Topildi:\n🎵 {title}\n🔗 {url}")
