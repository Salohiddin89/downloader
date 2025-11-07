import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from dotenv import load_dotenv
from keep_alive import keep_alive

from handlers import start, help, media, song

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_routers(start.router, help.router, media.router, song.router)


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Botni ishga tushirish"),
        BotCommand(command="help", description="Komandalar ro'yxati"),
        BotCommand(command="music", description="Audio yoki matndan musiqa topish"),
    ]
    await bot.set_my_commands(commands)


async def main():
    await set_commands(bot)
    await dp.start_polling(bot)


keep_alive()

if __name__ == "__main__":
    asyncio.run(main())
