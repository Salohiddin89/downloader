import os
import subprocess
from yt_dlp import YoutubeDL


def extract_info(url):
    ydl_opts = {"quiet": True}
    with YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)


def clean_mp3(filename):
    cleaned = filename.replace(".mp3", "_cleaned.mp3")
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            filename,
            "-vn",
            "-ar",
            "44100",
            "-ac",
            "2",
            "-b:a",
            "192k",
            cleaned,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return cleaned


async def download_video_or_audio(url, format_type="video"):
    os.makedirs("temp", exist_ok=True)

    ydl_opts = {
        "outtmpl": "temp/%(id)s.%(ext)s",
        "quiet": True,
        "no_warnings": True,
        "prefer_ffmpeg": True,
    }

    if format_type == "video":
        ydl_opts.update(
            {
                "format": "bv*+ba/best[ext=mp4]/best",
                "merge_output_format": "mp4",
                "postprocessors": [
                    {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}
                ],
            }
        )
    else:
        ydl_opts.update(
            {
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
            }
        )

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        ext = "mp3" if format_type == "audio" else "mp4"
        filename = f"temp/{info['id']}.{ext}"

        if not os.path.exists(filename):
            raise FileNotFoundError(f"❌ Fayl topilmadi: {filename}")

        # ✅ Audio faylni ffmpeg orqali tozalaymiz
        if format_type == "audio":
            cleaned = clean_mp3(filename)
            os.remove(filename)
            filename = cleaned

        return filename, info


def search_music(query):
    ydl_opts = {
        "quiet": True,
        "default_search": "ytsearch",
        "noplaylist": True,
        "skip_download": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        if "entries" in info and info["entries"]:
            entry = info["entries"][0]
            return entry["webpage_url"], entry["title"]
        else:
            return None, "Topilmadi"
