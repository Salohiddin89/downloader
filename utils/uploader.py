# import os
# from aiogram.types import FSInputFile

# from utils.downloader import download_audio


# async def send_audio(message, url, title):
#     filename, _ = download_audio(url)
#     if os.path.exists(filename):
#         await message.answer_audio(FSInputFile(filename), caption=f"🎵 {title}")
#         os.remove(filename)
#     else:
#         await message.answer("❌ Audio fayli topilmadi.")
