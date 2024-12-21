import msgpack
import logging
from consumer.handlers.form import handle_event_form
from consumer.handlers.like import handle_event_like
from consumer.handlers.recommendation import handle_event_recommendations

from consumer.schema.form import FormMessage
from consumer.metrics import TOTAL_RECEIVED_MESSAGES
from storage.rabbit import channel_pool
from logger import logger, LOGGING_CONFIG


async def start_consumer() -> None:
    queue_name = 'user_messages'
    logging.config.dictConfig(LOGGING_CONFIG)
    logger.info('Consumer starting...')
    async with channel_pool.acquire() as channel:
        await channel.set_qos(prefetch_count=10)
        queue = await channel.declare_queue(queue_name, durable=True)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                TOTAL_RECEIVED_MESSAGES.inc()
                async with message.process():
                    body = msgpack.unpackb(message.body)
                    if body['event'] == 'user_form':
                        await handle_event_form(body)
                    elif body['event'] == 'user_recommendations':
                        await handle_event_recommendations(body)
                    elif body['event'] == 'like':
                        await handle_event_like(body)
