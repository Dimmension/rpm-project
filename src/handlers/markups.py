from aiogram.types import ReplyKeyboardMarkup
from . import buttons
menu = ReplyKeyboardMarkup(
    keyboard=[[buttons.settings, buttons.meet]],
    resize_keyboard=True,
)
recommendation = ReplyKeyboardMarkup(
    keyboard=[[buttons.back_to_menu, buttons.dislike, buttons.like]],
    resize_keyboard=True,
)
settings = ReplyKeyboardMarkup(
    keyboard=[
        [buttons.change_profile],
        [buttons.delete_profile],
        [buttons.back_to_menu],
    ],
    resize_keyboard=True,
)