import msgpack
import logging
from consumer.handlers.form import handle_event_form
from consumer.handlers.like import handle_event_like
from consumer.handlers.recommendation import handle_event_recommendations
from storage.rabbit import channel_pool
from logger import logger, LOGGING_CONFIG
from consumer.metrics import TOTAL_RECEIVED_MESSAGES

async def start_consumer() -> None:
    logging.config.dictConfig(LOGGING_CONFIG)
    logger.info('Consumer starting...')
    queue_name = 'user_messages'
    async with channel_pool.acquire() as channel:
        await channel.set_qos(prefetch_count=10)
        queue = await channel.declare_queue(queue_name, durable=True)

        async with queue.iterator() as queue_iter:
            i=1
            async for message in queue_iter:
                TOTAL_RECEIVED_MESSAGES.inc(i)
                logger.info('____PROMETHEUS: ' + TOTAL_RECEIVED_MESSAGES)
                async with message.process():
                    body = msgpack.unpackb(message.body)
                    if body['event'] == 'user_form':
                        logger.info(f'User: {message.from_user} is filling out the form.')
                        await handle_event_form(body)
                    elif body['event'] == 'user_recommendations':
                        await handle_event_recommendations(body)
                    elif body['event'] == 'like':
                        await handle_event_like(body)

                        # TODO: использовать хэндлер для рекоммендаций
                        pass
    logger.info('Consumer stopping...')

