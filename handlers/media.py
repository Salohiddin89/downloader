from aiogram import Router, types
import re
import os
import shutil
from utils.downloader import extract_info, download_video_or_audio, search_music
from utils.music_detect import identify_music_with_pyzam
from utils.keyboard import media_menu, detect_button
from aiogram.filters import Command
from utils.keyboard import main_menu
from states.music_state import MusicSearch
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

# ✅ Faylni 5 daqiqadan keyin avtomatik o‘chirishni rejalashtiramiz
from cleanup_scheduler import schedule_file_deletion
import asyncio


router = Router()
user_video_data = {}
pending_files = {}  # user_id -> filename


# /music komandasi — FSMni faollashtiradi
@router.message(Command("music"))
async def handle_music_command(msg: types.Message, state: FSMContext):
    await msg.answer("🎧 Musiqa yuboring yoki nomini yozing:", reply_markup=main_menu)
    await state.set_state(MusicSearch.active)


# 🔙 Bosh menyuga qaytish — FSMni tugatadi
@router.message(lambda msg: msg.text == "🔙 Bosh menyuga qaytish")
async def exit_music_mode(msg: types.Message, state: FSMContext):
    await state.clear()
    await msg.answer("🏠 Siz bosh menyudasiz", reply_markup=types.ReplyKeyboardRemove())


@router.message(StateFilter(MusicSearch.active))
async def handle_music_input(msg: types.Message, state: FSMContext):
    current_state = await state.get_state()

    # ❌ Agar FSM holati yo‘q bo‘lsa — bu musiqa rejimi emas
    if current_state != MusicSearch.active:
        return  # Bot jim turadi

    # ✅ Endi faqat /music dan keyin kelgan xabarlar ishlanadi
    if msg.audio or msg.voice:
        file = msg.audio or msg.voice
        file_path = f"temp/{file.file_id}.ogg"
        await msg.bot.download(file, destination=file_path)

        # 🔔 Kutish xabari
        waiting_msg = await msg.answer("🔍 Qoshiqni qidiryapmiz... biroz kuting 🎶")

        result = await identify_music_with_pyzam(file_path)
        os.remove(file_path)

        if result:
            track = result["subtitle"]
            artist = result["title"]
            search_query = f"{track} - {artist}"

            link, _ = search_music(search_query)

            if link:
                audio_file, _ = await download_video_or_audio(link, format_type="audio")

                safe_name = f"{artist} - {track}".replace(" ", "_").replace("/", "_")
                new_path = f"temp/{safe_name}.mp3"
                shutil.move(audio_file, new_path)

                await msg.answer_audio(
                    types.FSInputFile(new_path),
                    caption=(
                        f"🎧 <b>Musiqa nomi:</b> <i>{artist}</i>\n"
                        f"🎤 <b>Ijrochi:</b> <i>{track}</i>"
                    ),
                    parse_mode="HTML",
                )
                os.remove(new_path)
            else:
                await msg.answer("🔗 Musiqa topilmadi.")

            # ✅ Har ikkala holatda ham kutish xabarini o‘chiramiz
            await msg.bot.delete_message(
                chat_id=msg.chat.id, message_id=waiting_msg.message_id
            )

        else:
            # ❌ Topilmadi — foydalanuvchiga tavsiya
            await msg.answer(
                "ℹ️ Qoshiqni aniqlash uchun trekni iloji boricha toza, fon shovqinsiz va original ritmda ayting."
            )

            # ❌ Kutish xabarini o‘chiramiz
            await msg.bot.delete_message(
                chat_id=msg.chat.id, message_id=waiting_msg.message_id
            )

    elif msg.text:
        query = msg.text.strip()
        link, title = search_music(query)

        if link:
            audio_file, _ = await download_video_or_audio(link, format_type="audio")

            # 🔍 title ni ajratamiz: "Artist - Track" formatda bo‘lsa
            if " - " in title:
                artist, track = title.split(" - ", 1)
            else:
                artist, track = "Noma’lum", title

            # 📁 Fayl nomini toza formatga o‘tkazamiz
            safe_name = f"{artist} - {track}".replace(" ", "_").replace("/", "_")
            new_path = f"temp/{safe_name}.mp3"
            shutil.move(audio_file, new_path)

            await msg.answer_audio(
                types.FSInputFile(new_path),
                caption=(
                    f"🎧 <b>Musiqa nomi:</b> <i>{track}</i>\n"
                    f"🎤 <b>Ijrochi:</b> <i>{artist}</i>"
                ),
                parse_mode="HTML",
            )
            os.remove(new_path)
        else:
            await msg.answer("❌ Musiqa topilmadi.")


@router.message(
    lambda msg: re.search(
        r"(https?://)?(www\.)?(youtube\.com|youtu\.be|instagram\.com|tiktok\.com)/[^\s]+",
        msg.text or "",
    )
)
async def handle_link(msg: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == MusicSearch.active:
        return  # 🎧 Musiqa rejimida bo‘lsa — linkni e’tiborsiz qoldiramiz

    url = msg.text.strip()
    loading_msg = await msg.answer("📥 Video haqida ma'lumot olinmoqda...")

    try:
        info = extract_info(url)
        title = (
            info.get("title")
            or info.get("description", "Noma’lum video").split("\n")[0]
        )
        thumb = info.get("thumbnail")

        sent = (
            await msg.answer_photo(
                thumb, caption=f"🎬 {title}", reply_markup=media_menu()
            )
            if thumb
            else await msg.answer(f"🎬 {title}", reply_markup=media_menu())
        )

        user_video_data[msg.from_user.id] = {
            "url": url,
            "title": title,
            "thumb_msg_id": sent.message_id,
        }

    except Exception as e:
        await msg.answer(f"❌ Xatolik: {e}")

    try:
        await msg.bot.delete_message(msg.chat.id, loading_msg.message_id)
    except:
        pass


@router.callback_query()
async def handle_callback(call: types.CallbackQuery):
    user_id = call.from_user.id
    data = user_video_data.get(user_id)
    if not data:
        await call.answer("❗ Avval video link yuboring.")
        return

    url = data["url"]
    title = data["title"]
    thumb_msg_id = data["thumb_msg_id"]

    await call.answer("⏳ Yuklanmoqda...")

    try:
        if call.data == "video":
            filename, _ = await download_video_or_audio(url, "video")
            pending_files[user_id] = filename

            # 🎬 Faylni foydalanuvchiga yuboramiz
            await call.message.answer_video(
                types.FSInputFile(filename),
                caption=f"🎬 {title}",
                reply_markup=detect_button("video", filename),
            )
            asyncio.create_task(schedule_file_deletion(filename, delay=60))

        elif call.data == "audio":
            filename, _ = await download_video_or_audio(url, "audio")
            pending_files[user_id] = filename
            await call.message.answer_audio(
                types.FSInputFile(filename),
                caption=f"🎵 {title}",
                reply_markup=detect_button("audio", filename),
            )

        elif call.data.startswith("detect:"):
            _, format_type, filename = call.data.split(":", 2)

            if not os.path.exists(filename):
                await call.message.answer("❌ Fayl topilmadi.")
                return

            loading_msg = await call.message.answer("🔍 Musiqa aniqlanmoqda...")
            result = await identify_music_with_pyzam(filename)
            os.remove(filename)

            try:
                await call.bot.delete_message(
                    call.message.chat.id, loading_msg.message_id
                )
            except:
                pass

            if result:
                title = f"{result['title']} - {result['subtitle']}"
                query = title

                # YouTube’dan qidiramiz
                link, found_title = search_music(query)

                if link:
                    audio_file, _ = await download_video_or_audio(
                        link, format_type="audio"
                    )
                    await call.message.answer_audio(
                        types.FSInputFile(audio_file), caption=f"🎧 {title}"
                    )
                    os.remove(audio_file)
                else:
                    await call.message.answer(f"🎧 {title}\n🔗 {result['url']}")
            else:
                await call.message.answer("❌ Musiqa aniqlanmadi.")

        # ✅ Bu qator tashqi try ichida bo‘lishi kerak
        try:
            await call.bot.delete_message(call.message.chat.id, thumb_msg_id)
        except Exception as e:
            pass

    except Exception as e:
        await call.message.answer(f"❌ Tugma ishlovida xatolik: {e}")
