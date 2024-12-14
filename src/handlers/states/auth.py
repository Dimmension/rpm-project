from aiogram.fsm.state import StatesGroup, State


class AuthGroup(StatesGroup):
    no_authorized = State()
    authorized = State()


class AuthForm(StatesGroup):
    photo = State()
    name = State()
    age = State()
    gender = State()
    description = State()
    filter_by_age = State()
    filter_by_gender = State()
    filter_by_description = State()
    photo = State()
