from shazamio import Shazam
import os


async def identify_music_with_pyzam(audio_path):
    if not os.path.exists(audio_path):
        print(f"❌ Fayl topilmadi: {audio_path}")
        return None

    try:
        shazam = Shazam()
        out = await shazam.recognize(audio_path)
        track = out.get("track")

        if not track:
            print("❌ Musiqa topilmadi.")
            return None

        return {
            "title": track.get("title"),
            "subtitle": track.get("subtitle"),
            "url": track.get("url"),
        }

    except Exception as e:
        print(f"❌ Aniqlashda xatolik: {e}")
        return None
