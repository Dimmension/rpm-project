import msgpack
import logging
from consumer.handlers.form import handle_event_form
from consumer.handlers.recommendations import handle_get_recommends
from consumer.handlers.like import handle_like_user
from consumer.schema.form import FormMessage
from storage.rabbit import channel_pool
from recsys.db import redis_manager

async def start_consumer() -> None:
    queue_name = 'user_messages'
    redis_manager.initialize_client()
    async with channel_pool.acquire() as channel:
        await channel.set_qos(prefetch_count=10)

        queue = await channel.declare_queue(queue_name, durable=True)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    body = msgpack.unpackb(message.body)
                    if body['event'] == 'user_form':
                        await handle_event_form(body)
                    elif body['event'] == 'recommendations':
                        await handle_get_recommends(body)
                    elif body['event'] == 'user_likes':
                        await handle_like_user(body)