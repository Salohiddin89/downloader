import asyncio
import os


async def schedule_file_deletion(filename: str, delay: int = 60):
    await asyncio.sleep(delay)
    if os.path.exists(filename):
        try:
            os.remove(filename)
            print(f"✅ Fayl o‘chirildi: {filename}")
        except Exception as e:
            print(f"❌ Faylni o‘chirishda xatolik: {e}")
