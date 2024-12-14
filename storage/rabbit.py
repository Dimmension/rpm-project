import aio_pika
from aio_pika.abc import AbstractRobustConnection
from aio_pika.pool import Pool

from config.settings import settings


async def get_connection() -> AbstractRobustConnection:
    return await aio_pika.connect_robust(settings.rabbit_url)


connection_pool: Pool = Pool(get_connection, max_size=2)


async def get_channel() -> aio_pika.Channel:
    async with connection_pool.acquire() as connection:
        return await connection.channel()


channel_pool: Pool = Pool(get_channel, max_size=10)


async def send_msg(exchange_name: str, queue_name: str, messages: list[bytes]) -> None:
    async with channel_pool.acquire() as channel:
        exchange = await channel.declare_exchange(
            exchange_name,
            aio_pika.ExchangeType.DIRECT,
            durable=True,
        )

        queue = await channel.declare_queue(queue_name, durable=True)
        await queue.bind(exchange, queue_name)

        for message in messages:
            # TODO: correlation_id
            await exchange.publish(aio_pika.Message(message), queue_name)
