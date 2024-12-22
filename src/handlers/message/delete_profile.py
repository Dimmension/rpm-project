import aio_pika
from aiogram import F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
import msgpack

from consumer.schema.form import DeleteFormMessage
from src.handlers import buttons
from src.handlers.markups import menu
from src.handlers.states.auth import AuthGroup
from src.handlers.states.profile import DeleteProfile
from storage import consts
from storage.rabbit import send_msg

from .router import router


@router.message(F.text == buttons.DELETE_PROFILE_MSG)
async def process_settings(message: Message, state: FSMContext) -> None:
    await state.set_state(DeleteProfile.deleting)
    markup = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text='Да'), KeyboardButton(text='Нет')]],
    )
    await message.answer(
        'Вы уверены, что хотите удалить ваш профиль?',
        reply_markup=markup,
    )


@router.message(F.text == 'Да', DeleteProfile.deleting)
async def process_delete_profile(message: Message, state: FSMContext) -> None:
    await state.clear()
    await send_msg(
        consts.EXCHANGE_NAME,
        consts.GENERAL_USERS_QUEUE_NAME,
        [
            aio_pika.Message(
                msgpack.packb(
                    DeleteFormMessage(
                        event='user_form',
                        action='delete_form',
                        user_id=message.from_user.id,
                    ),
                ),
            ),
        ]
    )
    await message.answer(
        'Ваш профиль успешно удален!',
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(F.text == 'Нет', DeleteProfile.deleting)
async def process_cancel_deletion(message: Message, state: FSMContext) -> None:
    await state.set_state(AuthGroup.authorized)
    await message.answer(
        'Аккаунт не удален, вы в меню',
        reply_markup=menu,
    )
