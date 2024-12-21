import msgpack
from consumer.handlers.form import handle_event_form
from consumer.handlers.recommendations import handle_get_recommends
from consumer.handlers.like import handle_like_user
from consumer.metrics import TOTAL_RECEIVED_MESSAGES
from storage.rabbit import channel_pool
from consumer.recsys.db import redis_manager
import logging.config
from consumer.logger import LOGGING_CONFIG, logger
logging.config.dictConfig(LOGGING_CONFIG)

async def start_consumer() -> None:
    logger.info('Consumer starting...')
    queue_name = 'user_messages'
    async with channel_pool.acquire() as channel:
        await channel.set_qos(prefetch_count=10)
        queue = await channel.declare_queue(queue_name, durable=True)
        logger.info(f'Set queue with name {queue_name}')
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                logger.info(f'Processing message: {message}')
                # TOTAL_RECEIVED_MESSAGES.inc()
                async with message.process():
                    body = msgpack.unpackb(message.body)
                    if body['event'] == 'user_form':
                        logger.info('Handling user form')
                        await handle_event_form(body)
                    elif body['event'] == 'recommendations':
                        logger.info('Handling user recommendations')
                        await handle_get_recommends(body)
                    elif body['event'] == 'user_likes':
                        logger.info('Handling user likes')
                        await handle_like_user(body)
    logger.info('Consumer stopping...')
