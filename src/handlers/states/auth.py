from aiogram.fsm.state import State, StatesGroup


class AuthGroup(StatesGroup):
    no_authorized = State()
    authorized = State()


class AuthProfileForm(StatesGroup):
    user_id = State()
    photo = State()
    username = State()
    age = State()
    gender = State()
    city = State()
    description = State()
    filter_by_age = State()
    filter_by_gender = State()
    filter_by_description = State()
