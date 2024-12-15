import asyncio
from typing import Any

import msgpack
import aio_pika
from aio_pika import Queue
from aio_pika import ExchangeType
from aio_pika.exceptions import QueueEmpty
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram import F

from config.settings import settings
from consumer.schema.like import LikeMessage
from .router import router
from ..states.recommend import DateGroup
from storage.rabbit import channel_pool
from storage.rabbit import send_msg


@router.message(F.text == '/find')
async def start_dating(message: Message, state: FSMContext) -> None:
    await message.answer('Началась подборка')
    await state.set_state(DateGroup.dating)

    async with channel_pool.acquire() as channel:
        queue: Queue = await channel.declare_queue(
            settings.USER_RECOMMENDATIONS_QUEUE_TEMPLATE.format(user_id=message.from_user.id),
            durable=True,
        )
        retries = 3
        for _ in range(retries):
            try:
                recommend = await queue.get()
                parsed_recommend: dict[str, Any] = msgpack.unpackb(recommend.body)
                markup = ReplyKeyboardMarkup(
                    keyboard=[
                        [KeyboardButton(text='💘'), KeyboardButton(text='💔')]
                    ],
                    resize_keyboard=True,
                    one_time_keyboard=True,
                )

                await message.answer(
                    text=f"\
                    Имя: {parsed_recommend['name']}\n \
                    Возраст: {parsed_recommend['age']}\n \
                    {parsed_recommend['description']}\n \
                    ",
                    reply_markup=markup,
                )
                print(parsed_recommend)
                await state.update_data(current_recommend=parsed_recommend)
                return
            except QueueEmpty:
                await asyncio.sleep(1)

        await message.answer('Нет рекомендаций')


@router.message(F.text == '💘')
async def like_candidate(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()
    current_recommend = state_data.get('current_recommend')

    if current_recommend:
        liked_user_id = current_recommend.get('user_id')

        send_msg(
            'user_messages', 
            settings.USER_LIKES_QUEUE_TEMPLATE.format(user_id=message.from_user.id),
            [
                aio_pika.Message(
                    msgpack.packb(
                        LikeMessage(
                            event='likes',
                            action='like_user',
                            user_id=message.from_user.id,
                            target_user_id=liked_user_id,
                        ),
                    ),
                )
            ]
        )
        async with channel_pool.acquire() as channel:
            likes_queue: Queue = await channel.declare_queue(
                settings.USER_LIKES_QUEUE_TEMPLATE.format(user_id=message.from_user.id),
                durable=True,
            )
            try:
                like = await likes_queue.get()
                parsed_like: dict[str, Any] = msgpack.unpackb(like.body)

                await message.answer(
                    text=f"У вас взаимные лайки с пользователем {parsed_like['user_like']}",
                )
                await show_next_candidate(message, state)
            except:
                await show_next_candidate(message, state)


@router.message(F.text == '💔')
async def dislike_candidate(message: Message, state: FSMContext) -> None:
    await message.answer("Вы пропустили этого пользователя")
    await show_next_candidate(message, state)


async def show_next_candidate(message: Message, state: FSMContext) -> None:
    async with channel_pool.acquire() as channel:
        queue: Queue = await channel.declare_queue(
            settings.USER_RECOMMENDATIONS_QUEUE_TEMPLATE.format(user_id=message.from_user.id),
            durable=True,
        )
        try:
            recommend = await queue.get()
            parsed_recommend: dict[str, Any] = msgpack.unpackb(recommend.body)

            markup = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text='💘'), KeyboardButton(text='💔')]
                ],
                resize_keyboard=True,
                one_time_keyboard=True,
            )

            await message.answer(
                text=f"\
                Имя: {parsed_recommend['name']}\n \
                Возраст: {parsed_recommend['age']}\n \
                {parsed_recommend['description']}\n \
                ",
                reply_markup=markup,
            )

            await state.update_data(current_recommend=parsed_recommend)

        except QueueEmpty:
            await message.answer('Нет рекомендаций')
