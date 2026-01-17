from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from datetime import datetime

from database import Database
from states import *
from keyboards import *

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, db: Database):
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
async def letter_chosen(message: Message, state: FSMContext):
    await state.update_data(chosen_letter=message.text)

    await message.answer("Отлично! Осталось последнее, введи свое имя и фамилию: ")
    await state.set_state(Registration.waiting_for_name)


@router.message(Registration.waiting_for_name)
async def name_chosen(message: Message, state: FSMContext, db: Database):
    if not message.from_user or not message.text:
        return
    user_data = await state.get_data()
    first_name = message.text.split()[0]
    last_name = message.text.split()[1]
    grade = user_data["chosen_grade"]
    letter = user_data["chosen_letter"]

    await db.register_user(
        message.from_user.id, first_name, last_name, int(grade), letter
    )

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
        f"<b>Имя:</b> {user['first_name']} {user['last_name']}\n"
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

    await message.answer(
        "Выберите день, на который задано домашнее задание:",
        reply_markup=get_date_selection_kb(),
    )

    await state.set_state(AddHomework.waiting_for_date)


@router.callback_query(F.data.startswith("date_"))
async def data_adding(callback: CallbackQuery, state: FSMContext):
    if not callback.message or not callback.data:
        return
    selected_date = callback.data.replace("date_", "")

    if selected_date == "manual":
        await callback.message.answer("Введите дату в формате ДД.ММ (например, 18.01):")
        await state.set_state(AddHomework.waiting_for_manual)
        return

    await state.update_data(date=selected_date)

    await callback.message.answer("Опубликовать анонимно?", reply_markup=get_anon_kb())
    await state.set_state(AddHomework.waiting_for_anon)

    await callback.answer()


@router.message(AddHomework.waiting_for_manual)
async def manual_data_adding(message: Message, state: FSMContext):
    await state.update_data(date=message.text)

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
        await message.answer(
            "<b>Упс!</b> Похоже, ты еще не зарегистрирован.\nДля регистрации напиши /start"
        )
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
        target_date=data["date"],
        author_id=message.from_user.id,
        is_anonymous=is_anon,
    )

    await message.answer(
        "✅ <b>Задание успешно добавлено!</b>", reply_markup=get_main_menu()
    )
    await state.clear()


@router.message(F.text == "📚 Узнать ДЗ")
async def show_homework(message: Message, db: Database):
    if not message.from_user:
        return

    user = await db.get_user(message.from_user.id)
    if not user:
        await message.answer(
            "<b>Упс!</b> Похоже, ты еще не зарегистрирован.\nДля регистрации напиши /start"
        )
        return

    homeworks = await db.get_homework_by_class(user["grade"], user["letter"])

    if not homeworks:
        await message.answer("<b>Новых заданий нет!</b> 🎉")
        return

    for hw in homeworks:
        has_sol = await db.check_solution_exists(hw["id"])

        date_str = hw["target_date"]
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        display_date = date_obj.strftime("%d.%m")

        if hw["is_anonymous"]:
            author_name = "Анонимно"
        else:
            author_data = await db.get_user(hw["author_id"])
            if author_data:
                author_name = f"{author_data['first_name']} {author_data['last_name']}"

        text = (
            f"📌 <b>Предмет:</b> {hw['subject_name']}\n"
            f"📝 <b>Задание:</b> {hw['text']}\n"
            f"⏳ <b>День:</b> {display_date}\n"
            f"👤 <b>Автор:</b> {author_name}"
        )

        if hw["photo_id"]:
            await message.answer_photo(
                hw["photo_id"],
                caption=text,
                reply_markup=get_hw_actions_kb(hw["id"], has_sol),
            )
        else:
            await message.answer(
                text, reply_markup=get_hw_actions_kb(hw["id"], has_sol)
            )


@router.callback_query(F.data.startswith("solve_"))
async def handle_solve_button(callback: CallbackQuery, state: FSMContext):
    if not callback.data or not callback.message:
        return
    hw_id = callback.data.split("_")[1]
    await state.update_data(current_hw_id=hw_id)

    await callback.message.answer("Отлично! Пришли текст решения или фото:")
    await state.set_state(AddSolution.waiting_for_content)
    await callback.answer()


@router.message(AddSolution.waiting_for_content)
async def solution_content_added(message: Message, state: FSMContext):
    if message.photo:
        await state.update_data(
            sol_text=message.caption, sol_photo=message.photo[-1].file_id
        )
    else:
        await state.update_data(sol_text=message.text, sol_photo=None)

    await message.answer("Опубликовать анонимно?", reply_markup=get_anon_kb())
    await state.set_state(AddSolution.waiting_for_anon)


@router.message(
    AddSolution.waiting_for_anon, F.text.in_(["Анонимно", "От своего имени"])
)
async def finish_solution(message: Message, state: FSMContext, db: Database):
    if not message.from_user:
        return

    is_anon = 1 if message.text == "Анонимно" else 0

    data = await state.get_data()

    await db.add_solution(
        hw_id=data["current_hw_id"],
        text=data["sol_text"],
        photo_id=data["sol_photo"],
        author_id=message.from_user.id,
        is_anonymous=is_anon,
    )

    await db.update_reputation(message.from_user.id, 5)


@router.callback_query(F.data.startswith("view_"))
async def view_solutions(callback: CallbackQuery, db: Database):
    hw_id = callback.data.split("_")[1]
    solutions = await db.get_solutions(hw_id)

    if not solutions:
        return

    await callback.answer(f"🔎 Найдено решений: {len(solutions)}")

    for sol in solutions:
        author_text = "Анонимно"
        if not sol["is_anonymous"]:
            user = await db.get_user(sol["author_id"])
            if user:
                author_text = f"{user['first_name']} {user['last_name']}"

        caption = f"✅ <b>Решение от:</b> {author_text}\n\n{sol['text'] or '<i>(Без текста)</i>'}"

        if sol["photo_id"]:
            await callback.message.answer_photo(
                sol["photo_id"],
                caption=caption,
                reply_markup=get_solution_votes_kb(sol["id"]),
            )
        else:
            await callback.message.answer(caption)

        await callback.answer()


@router.callback_query(F.data.startswith("vote_"))
async def handle_vote(callback: CallbackQuery, db: Database):
    parts = callback.data.split("_")
    action = parts[1]
    sol_id = parts[2]
    user_id = callback.from_user.id

    solution = await db.get_solution_by_id(sol_id)

    if solution["author_id"] == user_id:
        await callback.answer("Нельзя голосовать за свое решение!", show_alert=True)
        return

    vote_value = 1 if action == "up" else -1

    success = await db.add_vote(user_id, sol_id, vote_value)
    if not success:
        await callback.message.answer(
            "Вы уже голосовали за это решение!", show_alert=True
        )
        return

    await db.update_reputation(solution["author_id"], vote_value)

    ups, downs = await db.get_solution_votes(sol_id)

    new_kb = get_solution_votes_kb(sol_id, ups, downs)

    try:
        await callback.message.edit_reply_markup(reply_markup=new_kb)
    except Exception:
        pass

    await callback.answer("Голос учтен!")
