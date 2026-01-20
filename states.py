from aiogram.fsm.state import StatesGroup, State


class Registration(StatesGroup):
    waiting_for_grade = State()
    waiting_for_letter = State()
    waiting_for_name = State()
    waiting_for_confirm = State()


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


class BanUser(StatesGroup):
    waiting_for_ban_id = State()
    waiting_for_unban_id = State()
    waiting_for_promote_id = State()
    waiting_for_promote_status = State()


class SettingsStates(StatesGroup):
    waiting_for_new_grade = State()
    waiting_for_new_name = State()
