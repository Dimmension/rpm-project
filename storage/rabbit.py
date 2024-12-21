import aio_pika
from aio_pika.abc import AbstractRobustConnection
from aio_pika.pool import Pool

from config.settings import settings
from storage import consts


async def get_connection() -> AbstractRobustConnection:
    return await aio_pika.connect_robust(settings.rabbit_url)


connection_pool: Pool = Pool(get_connection, max_size=2)


async def get_channel() -> aio_pika.Channel:
    async with connection_pool.acquire() as connection:
        return await connection.channel()


channel_pool: Pool = Pool(get_channel, max_size=10)


async def send_msg(
    exchange_name: str,
    queue_name: str,
    messages: list[aio_pika.Message],
    user_id=None,
) -> None:
    async with channel_pool.acquire() as channel:
        exchange = await channel.declare_exchange(
            exchange_name,
            aio_pika.ExchangeType.DIRECT,
            durable=True,
        )

        queue = await channel.declare_queue(queue_name, durable=True)
        await queue.bind(exchange, queue_name)

        if user_id:
            user_queue = await channel.declare_queue(
                consts.USER_RECOMMENDATIONS_QUEUE_TEMPLATE.format(user_id=user_id),
                durable=True
            )
            await user_queue.bind(
                exchange,
                consts.USER_RECOMMENDATIONS_QUEUE_TEMPLATE.format(
                    user_id=user_id,
                ),
            )

        for message in messages:
            await exchange.publish(message, queue_name)