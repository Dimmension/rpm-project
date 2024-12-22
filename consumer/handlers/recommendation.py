import aio_pika
import msgpack
from aio_pika import ExchangeType
from neo4j import AsyncResult

from consumer.schema.recommendation import RecMessage
from storage import consts, queries
from storage.db import driver
from storage.rabbit import channel_pool


async def handle_event_recommendations(message: RecMessage):
    if message['action'] == 'get_recommendations':
        async with driver.session() as session:
            results: AsyncResult = await session.run(
                query=queries.GET_RECOMMENDATIONS,
                parameters={'user_id': message['user_id'], 'top_k': 10}
            )
            recommendations = await results.data()
            async with channel_pool.acquire() as channel: 
                exchange = await channel.declare_exchange(
                    consts.EXCHANGE_NAME,
                    ExchangeType.DIRECT,
                    durable=True,
                )
                for recommendation in recommendations:
                    recommendation['user_id'] = recommendation.pop('recommended_user_id')
                    await exchange.publish(
                        aio_pika.Message(
                            msgpack.packb(recommendation),
                            priority=consts.BASE_PRIORITY,
                        ),
                        routing_key=consts.USER_RECOMMENDATIONS_QUEUE_TEMPLATE.format(user_id=message['user_id']),
                    )