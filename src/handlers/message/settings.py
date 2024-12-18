from aiogram import F
from aiogram.types import Message, ReplyKeyboardMarkup

from src.handlers import buttons
from .router import router


@router.message(F.text == buttons.SETTINGS_MSG)
async def process_settings(message: Message) -> None:
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [buttons.change_profile],
            [buttons.delete_profile],
            [buttons.back_to_menu],
        ],
        resize_keyboard=True,
    )
    await message.answer(
        'Выберите подходящий пункт в настройках.',
        reply_markup=markup,
    )


@router.message(F.text == buttons.BACK_TO_MENU_MSG)
async def back_to_menu(message: Message) -> None:
    markup = ReplyKeyboardMarkup(
        keyboard=[[buttons.settings]],
        resize_keyboard=True,
    )
    await message.answer(
        'Вы в меню!',
        reply_markup=markup,
    )
