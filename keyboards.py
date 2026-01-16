from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_grade_kb():
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="8"),
                KeyboardButton(text="9"),
                KeyboardButton(text="10"),
                KeyboardButton(text="11"),
            ]
        ],
        resize_keyboard=True,
    )
    return kb


def get_letter_kb():
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="А"),
                KeyboardButton(text="Б"),
                KeyboardButton(text="В"),
            ]
        ],
        resize_keyboard=True,
    )
    return kb


def get_main_menu():
    kb = [
        [KeyboardButton(text="📚 Узнать ДЗ"), KeyboardButton(text="➕ Добавить ДЗ")],
        [KeyboardButton(text="🏆 Топ учеников"), KeyboardButton(text="👤 Профиль")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def get_subjects_kb(subjects):
    builder = ReplyKeyboardBuilder()
    for subject in subjects:
        builder.add(KeyboardButton(text=subject["name"]))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def get_skip_photo_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Пропустить фото")]], resize_keyboard=True
    )


def get_anon_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Анонимно"), KeyboardButton(text="От своего имени")]
        ],
        resize_keyboard=True,
    )
