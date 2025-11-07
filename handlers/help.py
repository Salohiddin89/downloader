from aiogram import Router, types
from aiogram.filters import Command

router = Router()


@router.message(Command("help"))
async def help(message: types.Message):
    await message.answer(
        "📚 Komandalar:\n\n"
        "/start - Botni ishga tushirish\n"
        "/help - Komandalar ro'yxati\n\n"
        "Link yuboring: YouTube, Instagram, TikTok\n"
        "Keyin tugmalar orqali video/audio/musiqa tanlang."
    )
