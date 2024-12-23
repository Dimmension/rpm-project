import asyncio
from typing import Any

import aio_pika
import msgpack
from aio_pika import Queue
from aio_pika.exceptions import QueueEmpty
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from consumer.schema.like import LikeMessage
from consumer.schema.recommendation import RecMessage
from src.handlers import buttons
from src.handlers.markups import recommendation
from src.services.minio_service import get_photo
from src.templates.env import render
from storage import consts, queries
from storage.db import driver
from storage import rabbit
from tests.mocking.rabbit import MockMessage

from .router import router


async def show_recommendations(message: Message, state: FSMContext) -> None:
    async with rabbit.channel_pool.acquire() as channel:
        queue: Queue = await channel.declare_queue(
            consts.USER_RECOMMENDATIONS_QUEUE_TEMPLATE.format(
                user_id=message.from_user.id,
            ),
            durable=True,
        )

        retries = 3
        for _ in range(retries):
            try:
                recommended_user = await queue.get()
                parsed_recommended_user: dict[str, Any] = msgpack.unpackb(
                    recommended_user.body,
                )

                if not isinstance(recommended_user, MockMessage):
                    await state.set_data(
                        {
                            'prev_user_id': parsed_recommended_user['user_id'],
                            'prev_user_priority': recommended_user.priority,
                            'prev_user_tag': parsed_recommended_user['user_tag'],
                        },
                    )
                text = render('user/user.jinja2', user=parsed_recommended_user)
                photo_file = await get_photo('main', parsed_recommended_user['user_id'])
                await message.answer_photo(photo_file, caption=text, reply_markup=recommendation)
                return
            except QueueEmpty:
                await asyncio.sleep(1)

        await rabbit.send_msg(
            consts.EXCHANGE_NAME,
            consts.GENERAL_USERS_QUEUE_NAME,
            [aio_pika.Message(
                msgpack.packb(
                    RecMessage(
                        event='user_recommendations',
                        action='get_recommendations',
                        user_id=message.from_user.id,
                    )
                ),
            ),]
        )
        await message.answer('Попробуйте позже или измените фильтры поиска.')


@router.message(F.text == buttons.MEET_MSG)
async def meet(message: Message, state: FSMContext) -> None:
    await show_recommendations(message, state)


@router.message(F.text == buttons.DISLIKE_MSG)
async def next_user(message: Message, state: FSMContext) -> None:
    await show_recommendations(message, state)


@router.message(F.text == buttons.LIKE_MSG)
async def like_user(message: Message, state: FSMContext) -> None:
    prev_user_id = await state.get_value('prev_user_id')
    prev_user_priority = await state.get_value('prev_user_priority')
    prev_user_tag = await state.get_value('prev_user_tag')

    if prev_user_priority == consts.LIKED_PRIORITY:
        await message.answer(f'Мэтч: @{prev_user_tag}')
        await rabbit.send_msg(
            consts.EXCHANGE_NAME,
            consts.GENERAL_USERS_QUEUE_NAME,
            [
                aio_pika.Message(
                    msgpack.packb(
                        LikeMessage(
                            event='like',
                            action='put_like',
                            user_id=message.from_user.id,
                            user_tag=message.from_user.username,
                            other_id=prev_user_id,
                        ),
                    ),
                ),
            ],
        )
        await show_recommendations(message, state)
        return

    async with driver.session() as session:
        results = await session.run(
            query=queries.GET_FOR_LIKES_USER_DATA,
            parameters={'user_id': message.from_user.id},
        )
        user_data = (await results.data())[0]
        await rabbit.send_msg(
            consts.EXCHANGE_NAME,
            consts.USER_RECOMMENDATIONS_QUEUE_TEMPLATE.format(
                user_id=prev_user_id,
            ),
            [aio_pika.Message(msgpack.packb(user_data), priority=consts.LIKED_PRIORITY)],
        )

    await show_recommendations(message, state)