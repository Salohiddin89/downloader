from aiogram import Router, types
from aiogram.filters import CommandStart

router = Router()


@router.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        f"👋 Salom, {message.from_user.full_name}!\n\n"
        "Menga YouTube, Instagram yoki TikTok linkini yuboring.\n"
        "Men sizga video, audio va fon musiqani topib beraman."
    )
