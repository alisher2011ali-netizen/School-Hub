from aiogram.fsm.state import StatesGroup, State


class Registration(StatesGroup):
    waiting_for_grade = State()
    waiting_for_letter = State()


class AddHomework(StatesGroup):
    waiting_for_subject = State()
    waiting_for_text = State()
    waiting_for_photo = State()
    waiting_for_anon = State()
