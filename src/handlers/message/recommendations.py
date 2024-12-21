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
from storage.consts import (
    USER_RECOMMENDATIONS_QUEUE_TEMPLATE, USER_LIKES_QUEUE_TEMPLATE,
    EXCHANGE_NAME, GENERAL_USERS_QUEUE_NAME, MIN_RECOMMENDATIONS_LIMIT,
)
from consumer.schema.like import LikeMessage
from consumer.schema.recommendation import RecMessage
import logging.config
from src.logger import LOGGING_CONFIG, logger
logging.config.dictConfig(LOGGING_CONFIG)

def get_reaction_buttons() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='💘'), KeyboardButton(text='💔')],
            [KeyboardButton(text='⏸️ Приостановить')],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

def get_control_buttons() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='▶️ Возобновить')],
            [KeyboardButton(text='/change_profile')],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

@router.message(F.text == '/find')
async def start_dating(message: Message, state: FSMContext) -> None:
    logger.info(f"User {message.from_user.id} started the dating process.")
    current_state = await state.get_state()
    if current_state == DateGroup.paused:
        logger.info(f"User {message.from_user.id} tried to start while paused.")
        await message.answer('Подборка уже приостановлена. Нажмите "Возобновить", чтобы продолжить.', reply_markup=get_control_buttons())
        return

    await message.answer('Началась подборка', reply_markup=get_control_buttons())
    await state.set_state(DateGroup.dating)

    async with channel_pool.acquire() as channel:
        logger.info(f"User {message.from_user.id}: Attempting to fetch recommendations.")
        queue: Queue = await channel.declare_queue(
            USER_RECOMMENDATIONS_QUEUE_TEMPLATE.format(user_id=message.from_user.id),
            durable=True,
        )
        retries = 3
        for _ in range(retries):
            try:
                recommend = await queue.get()
                parsed_recommend: dict[str, Any] = msgpack.unpackb(recommend.body)
                logger.info(f"User {message.from_user.id}: Recommendation fetched successfully.")
                markup = get_reaction_buttons()

                await message.answer(
                    text=f"{parsed_recommend['username']}\n{parsed_recommend['age']}\n{parsed_recommend['description']}",
                    reply_markup=markup,
                )
                await state.update_data(current_recommend=parsed_recommend)
                return
            except Exception as e:
                logger.error(f"User {message.from_user.id}: Error fetching recommendation - {e}")
                await asyncio.sleep(1)

        logger.warning(f"User {message.from_user.id}: No recommendations available.")
        await message.answer('Нет рекомендаций')

@router.message(F.text == '⏸️ Приостановить')
async def pause_dating(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state == DateGroup.dating:
        logger.info(f"User {message.from_user.id} paused the dating process.")
        await state.set_state(DateGroup.paused)
        await message.answer('Подборка приостановлена. Нажмите "Возобновить", чтобы продолжить.', reply_markup=get_control_buttons())
    else:
        logger.warning(f"User {message.from_user.id} tried to pause but was not in the dating state.")
        await message.answer('Подборка уже приостановлена или не запущена.')

@router.message(F.text == '▶️ Возобновить')
async def resume_dating(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state == DateGroup.paused:
        logger.info(f"User {message.from_user.id} resumed the dating process.")
        await state.set_state(DateGroup.dating)
        await message.answer('Продолжаем подборку.', reply_markup=get_reaction_buttons())
        await show_next_candidate(message, state)
    else:
        logger.warning(f"User {message.from_user.id} tried to resume but was not in the paused state.")
        await message.answer('Подборка не приостановлена или не запущена.')

@router.message(F.text == '💘')
async def like_candidate(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()
    current_recommend = state_data.get('current_recommend')

    if current_recommend:
        liked_user_id = current_recommend.get('user_id')
        logger.info(f"User {message.from_user.id} liked user {liked_user_id}.")

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
            try:
                like = await likes_queue.get()
                parsed_like: dict[str, Any] = msgpack.unpackb(like.body)
                logger.info(f"User {message.from_user.id} got a mutual like with user {parsed_like['target_user_id']}.")
                await message.answer(
                    text=f"У вас взаимные лайки с пользователем {parsed_like['target_user_id']}",
                )
                await show_next_candidate(message, state)
            except Exception as e:
                logger.error(f"User {message.from_user.id}: Error processing mutual like - {e}")

@router.message(F.text == '💔')
async def dislike_candidate(message: Message, state: FSMContext) -> None:
    logger.info(f"User {message.from_user.id} disliked the current candidate.")
    await show_next_candidate(message, state)

async def show_next_candidate(message: Message, state: FSMContext) -> None:
    async with channel_pool.acquire() as channel:
        logger.info(f"User {message.from_user.id}: Fetching the next candidate.")
        queue: Queue = await channel.declare_queue(
            USER_RECOMMENDATIONS_QUEUE_TEMPLATE.format(user_id=message.from_user.id),
            durable=True,
        )
        try:
            recommend = await queue.get()
            parsed_recommend: dict[str, Any] = msgpack.unpackb(recommend.body)
            logger.info(f"User {message.from_user.id}: Next candidate fetched successfully.")
            markup = get_reaction_buttons()

            await message.answer(
                text=f"{parsed_recommend['username']}\n{parsed_recommend['age']}\n{parsed_recommend['description']}",
                reply_markup=markup,
            )
            await state.update_data(current_recommend=parsed_recommend)
        except QueueEmpty:
            logger.warning(f"User {message.from_user.id}: No more candidates available.")
            await message.answer('Нет рекомендаций', reply_markup=get_control_buttons())

        if queue.method.message_count < MIN_RECOMMENDATIONS_LIMIT:
            logger.info(f"User {message.from_user.id}: Sending request for more recommendations.")
            send_msg(
                EXCHANGE_NAME,
                GENERAL_USERS_QUEUE_NAME,
                msgpack.packb(
                    RecMessage(
                        event='recommendations',
                        action='get_recommendations',
                        user_id=message.from_user.id,
                    )
                ),
            )
