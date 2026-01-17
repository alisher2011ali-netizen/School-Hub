from aiogram.fsm.state import StatesGroup, State


class Registration(StatesGroup):
    waiting_for_grade = State()
    waiting_for_letter = State()
    waiting_for_name = State()


class AddHomework(StatesGroup):
    waiting_for_subject = State()
    waiting_for_text = State()
    waiting_for_photo = State()
    waiting_for_date = State()
    waiting_for_manual = State()
    waiting_for_anon = State()


class AddSolution(StatesGroup):
    waiting_for_content = State()
    waiting_for_anon = State()
