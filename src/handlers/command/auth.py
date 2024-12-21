from aiogram import F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
import msgpack
from consumer.schema.form import FormMessage
from consumer.schema.recommendation import RecMessage
from src.handlers import buttons
from src.handlers.states.auth import AuthForm, AuthGroup
from src.handlers.command.router import router

from src.services.minio_service import upload_photo
from src.utils import validators

from storage.rabbit import send_msg
from storage import consts

import logging.config
from src.logger import LOGGING_CONFIG, logger
logging.config.dictConfig(LOGGING_CONFIG)

@router.message(F.text.in_(["/start", "/help"]))
async def start_or_help(message: Message, state: FSMContext) -> None:
    logger.info(f"User {message.from_user.id} started or requested help.")
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='/find')],
            [KeyboardButton(text='/change_profile')],
        ],
        resize_keyboard=True,
    )
    await message.answer(
        'Добро пожаловать! Выберите действие:',
        reply_markup=markup,
    )

@router.callback_query(F.data == buttons.AUTH_CALLBACK_MSG, AuthGroup.no_authorized)
async def auth(callback: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback.from_user.id} started the authorization process.")
    await state.set_state(AuthForm.photo)
    await callback.message.answer('*Загрузите фотографию для вашего профиля:')

@router.message(AuthForm.photo)
async def process_photo(message: Message, state: FSMContext) -> None:
    logger.info(f"User {message.from_user.id} is uploading a photo.")
    if message.content_type != 'photo':
        logger.warning(f"User {message.from_user.id} uploaded invalid photo format.")
        await message.answer('Неправильный формат фотографии!')
        return
    photo = message.photo[-1]
    file_name = f'user_{message.from_user.id}.jpg'
    bot = message.bot

    try:
        file_info = await bot.get_file(photo.file_id)
        file_bytes = await bot.download_file(file_info.file_path)

        await upload_photo('main', file_name, file_bytes.getvalue())
        logger.info(f"Photo for user {message.from_user.id} uploaded successfully.")
        await state.update_data(photo=file_name)
        await state.update_data(message_user_id=message.from_user.id)

        await state.set_state(AuthForm.name)
        await message.answer('*Введите имя')

    except Exception as e:
        logger.error(f"Error uploading photo for user {message.from_user.id}: {e}")
        await message.answer(f'Ошибка загрузки фотографии: {e}!')
        return

@router.message(AuthForm.name)
async def process_name(message: Message, state: FSMContext) -> None:
    logger.info(f"User {message.from_user.id} is entering their name.")
    valid_msg = validators.valid_username(message.text)
    if valid_msg:
        logger.warning(f"User {message.from_user.id} provided invalid name: {message.text}.")
        await message.answer(valid_msg)
        return

    await state.update_data(username=message.text)
    await state.set_state(AuthForm.age)
    await message.answer('*Введите возраст')

@router.message(AuthForm.age)
async def process_age(message: Message, state: FSMContext) -> None:
    logger.info(f"User {message.from_user.id} is entering their age.")
    valid_msg = validators.valid_age(message.text)
    if valid_msg:
        logger.warning(f"User {message.from_user.id} provided invalid age: {message.text}.")
        await message.answer(valid_msg)
        return

    await state.update_data(age=message.text)
    await state.set_state(AuthForm.gender)

    markup = InlineKeyboardMarkup(
        inline_keyboard=[[buttons.masculine, buttons.feminine]],
    )
    await message.answer(
        '*Выберите ваш пол',
        reply_markup=markup,
    )

@router.callback_query(
    F.data.in_({buttons.FEMININE_CALLBACK_MSG, buttons.MASCULINE_CALLBACK_MSG}),
    AuthForm.gender,
)
async def process_gender(callback: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback.from_user.id} selected gender: {callback.data}.")
    await state.update_data(gender=callback.data)
    await state.set_state(AuthForm.description)

    markup = InlineKeyboardMarkup(
        inline_keyboard=[[buttons.skip]]
    )

    await callback.message.answer(
        'Введите описание о себе',
        reply_markup=markup,
    )

@router.callback_query(
    F.data == buttons.SKIP_CALLBACK_MSG,
    AuthForm.description,
)
async def capture_description_callback(callback: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback.from_user.id} skipped description input.")
    await state.update_data(description=None)
    await _process_description(callback.message, state)

@router.message(AuthForm.description)
async def capture_description(message: Message, state: FSMContext) -> None:
    logger.info(f"User {message.from_user.id} is entering their description.")
    valid_msg = validators.valid_description(message.text)
    if valid_msg:
        logger.warning(f"User {message.from_user.id} provided invalid description: {message.text}.")
        await message.answer(valid_msg)
        return
    await state.update_data(description=message.text)
    await _process_description(message, state)

async def _process_description(message: Message, state: FSMContext) -> None:
    logger.info(f"User {message.from_user.id} is moving to filter by age.")
    await state.set_state(AuthForm.filter_by_age)

    markup = InlineKeyboardMarkup(inline_keyboard=[[buttons.skip]])
    await message.answer(
        'Укажите фильтр по возрасту (в формате: 18-36)',
        reply_markup=markup,
    )

@router.callback_query(
    F.data == buttons.SKIP_CALLBACK_MSG,
    AuthForm.filter_by_age,
)
async def capture_filter_by_age_callback(callback: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback.from_user.id} skipped age filter input.")
    await state.update_data(filter_by_age=None)
    await _process_filter_by_age(callback.message, state)

@router.message(AuthForm.filter_by_age)
async def capture_filter_by_age(message: Message, state: FSMContext) -> None:
    logger.info(f"User {message.from_user.id} is entering age filter.")
    valid_msg = validators.valid_filter_by_age(message.text)
    if valid_msg:
        logger.warning(f"User {message.from_user.id} provided invalid age filter: {message.text}.")
        await message.answer(valid_msg)
        return
    await state.update_data(filter_by_age=message.text)
    await _process_filter_by_age(message, state)

async def _process_filter_by_age(message: Message, state: FSMContext) -> None:
    logger.info(f"User {message.from_user.id} is moving to filter by gender.")
    await state.set_state(AuthForm.filter_by_gender)

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [buttons.masculine, buttons.feminine, buttons.no_preferences],
        ],
    )
    await message.answer(
        '*Выберите пол того, кого вы ищете',
        reply_markup=markup,
    )

@router.callback_query(
    F.data.in_({
        buttons.FEMININE_CALLBACK_MSG,
        buttons.MASCULINE_CALLBACK_MSG,
        buttons.NO_PREFERENCES_CALLBACK_MSG,
    }),
    AuthForm.filter_by_gender,
)
async def process_filter_by_gender(callback: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback.from_user.id} selected gender filter: {callback.data}.")
    await state.update_data(filter_by_gender=callback.data)
    await state.set_state(AuthForm.filter_by_description)

    markup = InlineKeyboardMarkup(inline_keyboard=[[buttons.skip]])
    await callback.message.answer(
        'Укажите описание, кого вы хотите найти',
        reply_markup=markup
    )

@router.callback_query(
    F.data == buttons.SKIP_CALLBACK_MSG,
    AuthForm.filter_by_description,
)
async def capture_filter_by_description_callback(callback: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"User {callback.from_user.id} skipped description filter input.")
    await state.update_data(filter_by_description=None)
    await _process_filter_by_description(callback.message, state)

@router.message(AuthForm.filter_by_description)
async def capture_filter_by_description(message: Message, state: FSMContext) -> None:
    logger.info(f"User {message.from_user.id} is entering description filter.")
    valid_msg = validators.valid_filter_by_description(message.text)
    if valid_msg:
        logger.warning(f"User {message.from_user.id} provided invalid description filter: {message.text}.")
        await message.answer(valid_msg)
        return
    await state.update_data(filter_by_description=message.text)
    await _process_filter_by_description(message, state)

async def _process_filter_by_description(message: Message, state: FSMContext) -> None:
    logger.info(f"User {message.from_user.id} completed profile setup.")
    form = {
        field: field_data
        for field, field_data in (await state.get_data()).items()
    }
    form['age'] = int(form['age'])
    await state.set_state(AuthGroup.authorized)
    logger.info(f"Sending profile data for user {message.from_user.id}.")
    await send_msg(
        consts.EXCHANGE_NAME,
        consts.GENERAL_USERS_QUEUE_NAME,
        [
            msgpack.packb(
                FormMessage(
                    event='user_form',
                    action='send_form',
                    user_id=str(form['message_user_id']),
                    **form,
                ),
            ),
            msgpack.packb(
                RecMessage(
                    event='recommendations',
                    action='get_recommendations',
                    user_id=str(form['message_user_id']),
                )
            ),
        ]
    )
    await _complete_registration(message)

async def _complete_registration(message: Message) -> None:
    logger.info(f"User {message.from_user.id} completed the registration.")
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='/find')],
            [KeyboardButton(text='/change_profile')],
        ],
        resize_keyboard=True,
    )
    await message.answer(
        'Теперь вы авторизованы. Выберите действие:',
        reply_markup=markup,
    )
