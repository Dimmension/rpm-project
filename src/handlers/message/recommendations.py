import asyncio
from typing import Any
import aio_pika
import msgpack
from aio_pika import Queue
from aio_pika.exceptions import QueueEmpty
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram import F

from config.settings import settings

from .router import router
from ..states.recommendations import DateGroup
from storage.rabbit import channel_pool, send_msg
from storage.consts import USER_RECOMMENDATIONS_QUEUE_TEMPLATE, USER_LIKES_QUEUE_TEMPLATE
from consumer.schema.like import LikeMessage

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@router.message(F.text == '/find')
async def start_dating(message: Message, state: FSMContext) -> None:
    
    await message.answer('Началась подборка')
    logging.info(f'FIND MESSAGE: {message}')
    await state.set_state(DateGroup.dating)

    async with channel_pool.acquire() as channel:
        queue: Queue = await channel.declare_queue(
            USER_RECOMMENDATIONS_QUEUE_TEMPLATE.format(user_id=message.from_user.id),
            durable=True,
        )
        print(queue)
        retries = 3
        for _ in range(retries):
            try:
                logging.info("PRE QUEUE")
                recommend = await queue.get()
                parsed_recommend: dict[str, Any] = msgpack.unpackb(recommend.body)
                logging.info(f"POST QUEUE {parsed_recommend}")
                markup = ReplyKeyboardMarkup(
                    keyboard=[
                        [KeyboardButton(text='💘'), KeyboardButton(text='💔')]
                    ],
                    resize_keyboard=True,
                    one_time_keyboard=True,
                )

                await message.answer(
                    text=f"{parsed_recommend['username']}\n{parsed_recommend['age']}\n{parsed_recommend['description']}",
                    reply_markup=markup,
                )
                # Сохраняем текущую рекомендацию в состоянии для обработки реакции
                await state.update_data(current_recommend=parsed_recommend)
                return
            except Exception as e:
                logging.warning(f'ERROR {e}')
                await asyncio.sleep(1)

        await message.answer('Нет рекомендаций')


@router.message(F.text == '💘')
async def like_candidate(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()
    current_recommend = state_data.get('current_recommend')

    if current_recommend:
        liked_user_id = current_recommend.get('user_id')

        await send_msg(
            'user_messages', 
            USER_LIKES_QUEUE_TEMPLATE.format(user_id=message.from_user.id),
            [
                msgpack.packb(
                    LikeMessage(
                        event='user_likes',
                        action='like_user',
                        user_id=message.from_user.id,
                        target_user_id=liked_user_id,
                    ),
                ),
            ]
        )
        async with channel_pool.acquire() as channel:
            likes_queue: Queue = await channel.declare_queue(
                USER_LIKES_QUEUE_TEMPLATE.format(user_id=message.from_user.id),
                durable=True,
            )
            like = await likes_queue.get()
            parsed_like: dict[str, Any] = msgpack.unpackb(like.body)
            logging.info(f"PARSED LIKE: {parsed_like}")
            await message.answer(
                text=f"У вас взаимные лайки с пользователем {parsed_like['target_user_id']}",
            )
            await show_next_candidate(message, state)


@router.message(F.text == '💔')
async def dislike_candidate(message: Message, state: FSMContext) -> None:
    await show_next_candidate(message, state)


async def show_next_candidate(message: Message, state: FSMContext) -> None:
    async with channel_pool.acquire() as channel:
        queue: Queue = await channel.declare_queue(
            USER_RECOMMENDATIONS_QUEUE_TEMPLATE.format(user_id=message.from_user.id),
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
                text=f"{parsed_recommend['username']}\n{parsed_recommend['age']}\n{parsed_recommend['description']}",
                reply_markup=markup,
            )
            await state.update_data(current_recommend=parsed_recommend)
        except QueueEmpty:
            await message.answer('Нет рекомендаций')