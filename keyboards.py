from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from datetime import datetime, timedelta


def get_confirm_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="✅ Да, верно"), KeyboardButton(text="❌ Нет")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


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
                KeyboardButton(text="Т"),
                KeyboardButton(text="М"),
                KeyboardButton(text="Э"),
            ],
            [
                KeyboardButton(text="А"),
                KeyboardButton(text="Я"),
            ],
        ],
        resize_keyboard=True,
    )
    return kb


def get_main_menu_kb():
    kb = [
        [KeyboardButton(text="📚 Узнать ДЗ"), KeyboardButton(text="➕ Добавить ДЗ")],
        [KeyboardButton(text="👥 Мой класс"), KeyboardButton(text="👤 Профиль")],
        [KeyboardButton(text="🏆 Топ учеников")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def get_subjects_kb(subjects):
    builder = ReplyKeyboardBuilder()
    for subject in subjects:
        builder.add(KeyboardButton(text=subject["name"]))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def get_skip_photo_kb():
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Пропустить фото")],
            [KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
    )


def get_anon_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Анонимно"), KeyboardButton(text="От своего имени")]
        ],
        resize_keyboard=True,
    )


def get_hw_actions_kb(hw_id, has_solution=False):
    buttons = [
        [
            InlineKeyboardButton(
                text="➕ Добавить решение", callback_data=f"solve_{hw_id}"
            )
        ]
    ]
    if has_solution:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="📖 Посмотреть решения", callback_data=f"view_{hw_id}"
                )
            ]
        )
    buttons.append(
        [
            InlineKeyboardButton(
                text="🚩 Пожаловаться", callback_data=f"report_hw_{hw_id}"
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_date_selection_kb():
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    after_tomorrow = today + timedelta(days=2)

    kb = [
        [
            InlineKeyboardButton(
                text="На завтра", callback_data=f"date_{tomorrow.strftime("%Y-%m-%d")}"
            ),
            InlineKeyboardButton(
                text="На послезавтра",
                callback_data=f"date_{after_tomorrow.strftime("%Y-%m-%d")}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Другой день (внести вручную)", callback_data="date_manual"
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_solution_votes_kb(sol_id, ups=0, downs=0):
    kb = [
        [
            InlineKeyboardButton(text=f"👍 {ups}", callback_data=f"vote_up_{sol_id}"),
            InlineKeyboardButton(
                text=f"👎 {downs}", callback_data=f"vote_down_{sol_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                text="🚩 Пожаловаться", callback_data=f"report_sol_{sol_id}"
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_finish_content_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Готово ✅")],
            [KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
    )


def get_cancel_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def get_settings_change_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📝 Изменить класс", callback_data="change_grade"
                ),
                InlineKeyboardButton(
                    text="📝 Изменить имя", callback_data="change_name"
                ),
            ]
        ]
    )
