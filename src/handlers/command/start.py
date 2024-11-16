from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from src.handlers.states.auth import AuthGroup

from .router import router


@router.message(Command('start'), AuthGroup.authorized)
async def start_cmd(message: Message, state: FSMContext) -> None:
    await message.answer('Выберите следующие пункты')


@router.message(Command('start'))
async def start_cmd(message: Message, state: FSMContext) -> None:
    await state.set_state(AuthGroup.no_authorized)
    auth_button = InlineKeyboardButton(text='/auth', callback_data='/auth')
    markup = InlineKeyboardMarkup(inline_keyboard=[[auth_button]])
    await message.answer(
        'Вам необходимо авторизоваться',
        reply_markup=markup,
    )
