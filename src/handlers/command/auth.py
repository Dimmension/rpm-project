"""Обработка формы авторизации"""
from aio_pika import ExchangeType
import aio_pika
from aiogram import F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
import msgpack

from config.settings import settings
from consumer.schema.form import FormMessage, RecommendMessage
from src.handlers.states.auth import AuthForm, AuthGroup
from src.handlers.command.router import router

from src.storage.rabbit import channel_pool


# TODO: добавить опциональные поля в форму
@router.callback_query(F.data == '/auth', AuthGroup.no_authorized)
async def auth(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AuthForm.name)
    await callback.message.answer('Введите имя')


@router.message(AuthForm.name)
async def process_name(message: Message, state: FSMContext) -> None:
    # TODO: Сделать валидацию имени
    await state.update_data(name=message)
    await state.set_state(AuthForm.age)
    await message.answer('Введите возраст')


@router.message(AuthForm.age)
async def process_age(message: Message, state: FSMContext) -> None:
    # TODO: вынести в отдельную функцию (использовать регулярки)
    if not message.text.isdigit():
        await message.answer('Неправильный возраст')
        return

    await state.update_data(age=message)
    await state.set_state(AuthForm.gender)
    masculine_button = InlineKeyboardButton(
        text='Мужчина',
        callback_data='masculine',
    )
    feminine_button = InlineKeyboardButton(
        text='Женщина',
        callback_data='feminine',
    )
    markup = InlineKeyboardMarkup(
        inline_keyboard=[[masculine_button, feminine_button]],
    )
    await message.answer(
        'Выберите ваш пол',
        reply_markup=markup,
    )


@router.callback_query(F.data.in_({'feminine', 'masculine'}), AuthForm.gender)
async def process_gender(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(gender=callback.message)
    await state.set_state(AuthForm.description)
    await callback.message.answer('Введите описание о себе')


@router.message(AuthForm.description)
async def process_description(message: Message, state: FSMContext) -> None:
    # TODO: сделать валидацию описания
    await state.update_data(description=message)
    await state.set_state(AuthForm.filter_by_age)
    await message.answer('Укажите фильтр по возрасту (в формате: 18-36)')


@router.message(AuthForm.filter_by_age)
async def process_filter_by_age(message: Message, state: FSMContext) -> None:
    # TODO: сделать валидацию фильтра по возрасту
    await state.update_data(filter_by_age=message)
    await state.set_state(AuthForm.filter_by_gender)
    # TODO: избавиться от DRY
    masculine_button = InlineKeyboardButton(
        text='мужчина',
        callback_data='masculine',
    )
    feminine_button = InlineKeyboardButton(
        text='женщина',
        callback_data='feminine',
    )
    no_preferences_button = InlineKeyboardButton(
        text='все',
        callback_data='all',
    )
    markup = InlineKeyboardMarkup(
        inline_keyboard=[[masculine_button, feminine_button, no_preferences_button]],
    )
    await message.answer(
        'Выберите пол того, кого вы ищете',
        reply_markup=markup,
    )


@router.callback_query(
    F.data.in_({'feminine', 'masculine', 'all'}),
    AuthForm.filter_by_gender,
)
async def process_filter_by_gender(callback: CallbackQuery, state: FSMContext) -> None:
    # TODO: сделать валидацию фильтра по полу
    await state.update_data(filter_by_gender=callback.message)
    await state.set_state(AuthForm.filter_by_description)
    await callback.message.answer('Укажите описание, кого вы хотите найти')


@router.message(AuthForm.filter_by_description)
async def process_filter_by_description(message: Message, state: FSMContext) -> None:
    # TODO: валидация фильтра по описанию
    form = await state.update_data(filter_by_description=message)
    form = {field: field_data.text for field, field_data in form.items()}
    form['age'] = int(form['age'])

    await state.set_state(AuthGroup.authorized)

    # TODO: вынести в отдельную функцию
    # НАЧАЛО: создание очереди для пользователя + отправка анкеты
    async with channel_pool.acquire() as channel:
        exchange = await channel.declare_exchange(
            'user_recommendations',
            ExchangeType.DIRECT,
            durable=True,
        )

        queue = await channel.declare_queue(
            settings.USER_RECOMMENDATIONS_QUEUE_TEMPLATE.format(
                user_id=message.from_user.id,
            ),
            durable=True,
        )

        users_queue = await channel.declare_queue(
            'user_messages',
            durable=True,
        )

        await queue.bind(
            exchange,
            settings.USER_RECOMMENDATIONS_QUEUE_TEMPLATE.format(
                user_id=message.from_user.id,
            ),
        )

        await users_queue.bind(
            exchange,
            'user_messages',
        )

        # TODO: переименовать action и event
        await exchange.publish(
            aio_pika.Message(
                msgpack.packb(
                    FormMessage(
                        event='user_form',
                        action='send_form',
                        user_id=message.from_user.id,
                        **form,
                    ),
                ),
                # TODO: correlation_id
            ),
            'user_messages',
        )

        await exchange.publish(
            aio_pika.Message(
                msgpack.packb(
                    RecommendMessage(
                        user_id=message.from_user.id,
                        action='get_recommends',
                        event='recommendations',
                    ),
                ),
            ),
            'user_messages',
        )
    # КОНЕЦ: создание очереди для пользователя + отправка анкеты

    await message.answer('Теперь вы авторизованы')
    # TODO: сделать заполнение очереди с рекомендациями
