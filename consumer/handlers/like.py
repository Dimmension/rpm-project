
import aio_pika
import msgpack
import logging

from recsys.db import redis_manager
from storage.rabbit import send_msg
from storage.consts import USER_LIKES_QUEUE_TEMPLATE

async def handle_like_user(message):
    if message['action'] == 'like_user':
        redis_manager.add_user_like(message)
        if await redis_manager.check_user_likes(message):
            await send_msg(
                'user_likes',
                USER_LIKES_QUEUE_TEMPLATE.format(user_id=message['user_id']),
                aio_pika.Message(msgpack.packb({'user_like': message['target_user_id']})),
            )
            await send_msg(
                'user_likes',
                USER_LIKES_QUEUE_TEMPLATE.format(user_id=message['target_user_id']),
                aio_pika.Message(msgpack.packb({'user_like': message['user_id']})),
            )
            logging.info(f"Match notification sent for users {message['user_id']} and {message['target_user_id']}.")