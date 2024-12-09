import asyncio
from typing import Any

import msgpack
from aio_pika import Queue
from aio_pika.exceptions import QueueEmpty
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram import F

from config.settings import settings

from .router import router
from ..states.recommend import DateGroup
from ...storage.rabbit import channel_pool

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

                # Создаем клавиатуру с двумя кнопками
                markup = ReplyKeyboardMarkup(
                    keyboard=[
                        [KeyboardButton(text='💘'), KeyboardButton(text='💔')]
                    ],
                    resize_keyboard=True,
                    one_time_keyboard=True,
                )

                await message.answer(
                    text=f"{parsed_recommend['name']}\n{parsed_recommend['age']}\n{parsed_recommend['description']}",
                    reply_markup=markup,
                )
                # Сохраняем текущую рекомендацию в состоянии для обработки реакции
                await state.update_data(current_recommend=parsed_recommend)
                return
            except QueueEmpty:
                await asyncio.sleep(1)

        await message.answer('Нет рекомендаций')


@router.message(F.text == '💘')
async def like_candidate(message: Message, state: FSMContext) -> None:
    await show_next_candidate(message, state)


@router.message(F.text == '💔')
async def dislike_candidate(message: Message, state: FSMContext) -> None:
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
                text=f"{parsed_recommend['name']}\n{parsed_recommend['age']}\n{parsed_recommend['description']}",
                reply_markup=markup,
            )
            # Сохраняем текущую рекомендацию в состоянии
            await state.update_data(current_recommend=parsed_recommend)
        except QueueEmpty:
            await message.answer('Нет рекомендаций')
