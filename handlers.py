from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from database import Database
from states import *
from keyboards import *

router = Router()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext, db: Database):
    if not message.from_user:
        return
    user = await db.get_user(message.from_user.id)

    if user:
        await message.answer(
            f"Ты уже зарегистрирован. Твой класс: {user['grade']}-{user['letter']}",
            reply_markup=get_main_menu(),
        )
        return

    await message.answer(
        "Добро пожаловать в School Hub! Из какого ты класса?",
        reply_markup=get_grade_kb(),
    )
    await state.set_state(Registration.waiting_for_grade)


@router.message(Registration.waiting_for_grade)
async def grade_chosen(message: Message, state: FSMContext):
    await state.update_data(chosen_grade=message.text)

    await message.answer("Отлично! А какая буква?", reply_markup=get_letter_kb())
    await state.set_state(Registration.waiting_for_letter)


@router.message(Registration.waiting_for_letter)
async def letter_chosen(message: Message, state: FSMContext, db: Database):
    if not message.from_user:
        return
    user_data = await state.get_data()
    grade = user_data["chosen_grade"]
    letter = message.text

    await db.register_user(message.from_user.id, int(grade), letter)

    await message.answer(
        f"Регистрация завершена! Класс: {grade}-{letter}",
        reply_markup=ReplyKeyboardRemove(),
    )

    await message.answer("Выбирай действие:", reply_markup=get_main_menu())
    await state.clear()


@router.message(F.text == "👤 Профиль")
async def show_profile(message: Message, db: Database):
    if not message.from_user:
        return
    user = await db.get_user(message.from_user.id)

    if not user:
        await message.answer(
            "<b>Упс!</b> Похоже, ты еще не зарегистрирован.\nДля регистрации напиши /start"
        )
        return

    text = (
        f"👤 <b>Твой профиль</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"🏫 <b>Класс:</b> {user['grade']}-{user['letter']}\n"
        f"🌟 <b>Репутация:</b> <code>{user['reputation']}</code>\n"
        f"🆔 <b>ID:</b> <code>{user['user_id']}</code>\n\n"
        f"<i>Статус: {'Администратор' if user['is_admin'] else 'Ученик'}</i>"
    )

    await message.answer(text)


@router.message(F.text == "➕ Добавить ДЗ")
async def start_add_hw(message: Message, state: FSMContext, db: Database):
    subjects = await db.get_subjects()
    await message.answer(
        "<b>Выберите предмет:</b>", reply_markup=get_subjects_kb(subjects)
    )
    await state.set_state(AddHomework.waiting_for_subject)


@router.message(AddHomework.waiting_for_subject)
async def hw_subject_chosen(message: Message, state: FSMContext):
    await state.update_data(subject_name=message.text)
    await message.answer("Введите текст задания: ", reply_markup=ReplyKeyboardRemove())
    await state.set_state(AddHomework.waiting_for_text)


@router.message(AddHomework.waiting_for_text)
async def hw_text_added(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await message.answer(
        'Отправьте фото (если есть) или нажмите "Пропустить":',
        reply_markup=get_skip_photo_kb(),
    )

    await state.set_state(AddHomework.waiting_for_photo)


@router.message(AddHomework.waiting_for_photo, F.photo | (F.text == "Пропустить фото"))
async def photo_added(message: Message, state: FSMContext):
    if message.photo:
        await state.update_data(photo_id=message.photo[-1].file_id)
    else:
        await state.update_data(photo_id=None)

    await message.answer("Опубликовать анонимно?", reply_markup=get_anon_kb())
    await state.set_state(AddHomework.waiting_for_anon)


@router.message(
    AddHomework.waiting_for_anon, F.text.in_(["Анонимно", "От своего имени"])
)
async def save_homework(message: Message, state: FSMContext, db: Database):
    if not message.from_user:
        return

    data = await state.get_data()
    user = await db.get_user(message.from_user.id)

    if not user:
        return

    subject = await db.get_subject_by_name(data["subject_name"])
    if not subject:
        return

    is_anon = 1 if message.text == "Анонимно" else 0
    await db.add_homework(
        subject_id=subject["id"],
        grade=user["grade"],
        letter=user["letter"],
        text=data["text"],
        photo_id=data["photo_id"],
        author_id=message.from_user.id,
        is_anonymous=is_anon,
    )

    await message.answer(
        "✅ <b>Задание успешно добавлено!</b>", reply_markup=get_main_menu()
    )
    await state.clear()
