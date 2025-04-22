from aiogram.fsm.state import State, StatesGroup


class EditProfileForm(StatesGroup):
    photo = State()
    username = State()
    age = State()
    city = State()
    gender = State()
    description = State()
    filter_by_age = State()
    filter_by_gender = State()
    filter_by_description = State()
class DeleteProfile(StatesGroup):
    deleting = State()