
import aio_pika
import msgpack
from aio_pika import ExchangeType

from config.settings import settings
from recommend_system.chroma import chroma_manager
from consumer.schema.like import LikeMessage
from storage.rabbit import channel_pool

async def handle_like_user(message: LikeMessage):
    if message['action'] == 'like_user':
        chroma_manager.add_user_like(message)
        if chroma_manager.check_user_likes(message):
            async with channel_pool.acquire() as channel:
                exchange = await channel.declare_exchange("user_likes", ExchangeType.DIRECT, durable=True)
                
                await exchange.publish(
                    aio_pika.Message(
                        msgpack.packb({'user_like': message['target_user_id']}),
                    ),
                    routing_key=settings.USER_LIKES_QUEUE_TEMPLATE.format(user_id=message['user_id']),
                )
  
                await exchange.publish(
                    aio_pika.Message(
                        msgpack.packb({'user_like': message['user_id']}),
                    ),
                    routing_key=settings.USER_LIKES_QUEUE_TEMPLATE.format(user_id=message['target_user_id']),
                )