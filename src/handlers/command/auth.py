import aio_pika
import msgpack
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from config.settings import settings
from consumer.schema.form import FormMessage
from consumer.schema.recommendation import RecMessage
from src.handlers import buttons
from src.handlers.command.router import router
from src.handlers.markups import menu
from src.handlers.states.auth import AuthGroup, AuthProfileForm
from src.services.minio_service import upload_photo
from src.utils import validators
from storage import consts
from storage.rabbit import send_msg


@router.callback_query(F.data == buttons.AUTH_CALLBACK_MSG, AuthGroup.no_authorized)
async def auth(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AuthProfileForm.photo)
    await callback.message.answer('*Загрузите фотографию для вашего профиля:')


@router.message(AuthProfileForm.photo)
async def process_photo(message: Message, state: FSMContext) -> None:
    if message.content_type != 'photo':
        await message.answer('Неправильный формат фотографии!')
        return
    photo = message.photo[-1]
    file_name = f'user_{message.from_user.id}.jpg'
    bot = message.bot

    try:
        file_info = await bot.get_file(photo.file_id)
        file_bytes = await bot.download_file(file_info.file_path)

        await upload_photo(settings.MINIO_BUCKET_NAME, file_name, file_bytes.getvalue())
        await state.update_data(
            {
                'photo': file_name,
                'user_id': message.from_user.id,
                'user_tag': message.from_user.username,
            },
        )

        await state.set_state(AuthProfileForm.username)
        await message.answer('*Введите имя')

    except Exception as e:
        await message.answer(f'Ошибка загрузки фотографии: {e}!')
        return


@router.message(AuthProfileForm.username)
async def process_username(message: Message, state: FSMContext) -> None:
    valid_msg = validators.valid_username(message.text)
    if valid_msg:
        await message.answer(valid_msg)
        return

    await state.update_data(username=message.text)
    await state.set_state(AuthProfileForm.age)
    await message.answer('*Введите возраст')


@router.message(AuthProfileForm.age)
async def process_age(message: Message, state: FSMContext) -> None:
    valid_msg = validators.valid_age(message.text)
    if valid_msg:
        await message.answer(valid_msg)
        return

    await state.update_data(age=message.text)
    await state.set_state(AuthProfileForm.gender)

    markup = InlineKeyboardMarkup(
        inline_keyboard=[[buttons.masculine, buttons.feminine]],
    )
    await message.answer(
        '*Выберите ваш пол',
        reply_markup=markup,
    )


@router.callback_query(
    F.data.in_({buttons.FEMININE_CALLBACK_MSG, buttons.MASCULINE_CALLBACK_MSG}),
    AuthProfileForm.gender,
)
async def process_gender(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(gender=callback.data)
    await state.set_state(AuthProfileForm.city)

    await callback.message.answer('*Введите ваш город с заглавной буквы (если название города состоит из нескольких слов, через тире: Санкт-Петербург и.т.п.)')


@router.message(AuthProfileForm.city)
async def capture_city(message: Message, state: FSMContext) -> None:
    valid_msg = validators.valid_city(message.text)
    if valid_msg:
        await message.answer(valid_msg)
        return
    await state.update_data(city=message.text)
    await _process_city(message, state)


async def _process_city(message: Message, state: FSMContext) -> None:
    await state.set_state(AuthProfileForm.description)

    markup = InlineKeyboardMarkup(
        inline_keyboard=[[buttons.skip]]
    )

    await message.answer(
        'Введите описание о себе',
        reply_markup=markup,
    )


@router.callback_query(
    F.data == buttons.SKIP_CALLBACK_MSG,
    AuthProfileForm.description,
)
async def capture_description_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(description=None)
    await _process_description(callback.message, state)


@router.message(AuthProfileForm.description)
async def capture_description(message: Message, state: FSMContext) -> None:
    valid_msg = validators.valid_description(message.text)
    if valid_msg:
        await message.answer(valid_msg)
        return
    await state.update_data(description=message.text)
    await _process_description(message, state)


async def _process_description(message: Message, state: FSMContext) -> None:
    await state.set_state(AuthProfileForm.filter_by_age)

    markup = InlineKeyboardMarkup(inline_keyboard=[[buttons.skip]])
    await message.answer(
        'Укажите фильтр по возрасту (в формате: 18-36)',
        reply_markup=markup,
    )


@router.callback_query(
    F.data == buttons.SKIP_CALLBACK_MSG,
    AuthProfileForm.filter_by_age,
)
async def capture_filter_by_age_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(filter_by_age=None)
    await _process_filter_by_age(callback.message, state)


@router.message(AuthProfileForm.filter_by_age)
async def capture_filter_by_age(message: Message, state: FSMContext) -> None:
    valid_msg = validators.valid_filter_by_age(message.text)
    if valid_msg:
        await message.answer(valid_msg)
        return
    await state.update_data(filter_by_age=message.text)
    await _process_filter_by_age(message, state)


async def _process_filter_by_age(message: Message, state: FSMContext) -> None:
    await state.set_state(AuthProfileForm.filter_by_gender)

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
    AuthProfileForm.filter_by_gender,
)
async def process_filter_by_gender(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(filter_by_gender=callback.data)
    await state.set_state(AuthProfileForm.filter_by_description)

    markup = InlineKeyboardMarkup(inline_keyboard=[[buttons.skip]])
    await callback.message.answer(
        'Укажите описание, кого вы хотите найти',
        reply_markup=markup
    )


@router.callback_query(
    F.data == buttons.SKIP_CALLBACK_MSG,
    AuthProfileForm.filter_by_description,
)
async def capture_filter_by_description_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(filter_by_description=None)
    await _process_filter_by_description(callback.message, state)


@router.message(AuthProfileForm.filter_by_description)
async def capture_filter_by_description(message: Message, state: FSMContext) -> None:
    valid_msg = validators.valid_filter_by_description(message.text)
    if valid_msg:
        await message.answer(valid_msg)
        return
    await state.update_data(filter_by_description=message.text)
    await _process_filter_by_description(message, state)


async def _process_filter_by_description(message: Message, state: FSMContext) -> None:
    form: dict[str, str | int] = {
        field: field_data
        for field, field_data in (await state.get_data()).items()
    }
    form['age'] = int(form['age'])
    form['user_id'] = int(form['user_id'])

    filter_by_age_field = form.pop('filter_by_age')
    if filter_by_age_field:
        age_min, age_max = map(int, filter_by_age_field.split('-'))
    else:
        age_min = age_max = None

    form['filter_by_age_min'] = age_min
    form['filter_by_age_max'] = age_max

    await state.set_state(AuthGroup.authorized)
    await send_msg(
        consts.EXCHANGE_NAME,
        consts.GENERAL_USERS_QUEUE_NAME,
        [
            aio_pika.Message(
                msgpack.packb(
                    FormMessage(
                        event='user_form',
                        action='send_form',
                        **form,
                    ),
                ),
            ),
            aio_pika.Message(
                msgpack.packb(
                    RecMessage(
                        event='user_recommendations',
                        action='get_recommendations',
                        user_id=form['user_id'],
                    )
                ),
            ),
        ],
        user_id=form['user_id'],
    )
    await message.answer(
        'Теперь вы авторизованы',
        reply_markup=menu,
    )
