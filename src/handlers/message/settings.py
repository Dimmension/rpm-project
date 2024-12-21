from aiogram import F
from aiogram.types import Message

from src.handlers import buttons, markups
from .router import router


@router.message(F.text == buttons.SETTINGS_MSG)
async def process_settings(message: Message) -> None:
    await message.answer(
        'Выберите подходящий пункт в настройках.',
        reply_markup=markups.settings,
    )


@router.message(F.text == buttons.BACK_TO_MENU_MSG)
async def back_to_menu(message: Message) -> None:
    await message.answer(
        'Вы в меню!',
        reply_markup=markups.menu,
    )