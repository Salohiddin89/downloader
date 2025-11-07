from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def media_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎬 Video yuklash", callback_data="video")],
            [InlineKeyboardButton(text="🎵 Audio yuklash", callback_data="audio")],
            [InlineKeyboardButton(text="📄 Sarlavha", callback_data="title")],
        ]
    )


def detect_button(format_type, filename):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎶 Qoshiqni topish",
                    callback_data=f"detect:{format_type}:{filename}",
                )
            ]
        ]
    )

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔙 Bosh menyuga qaytish")]
    ],
    resize_keyboard=True
)
