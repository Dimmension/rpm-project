
import aio_pika
import msgpack
from aio_pika import ExchangeType

from config.settings import settings
from recommend_system.chroma import chroma_manager
from consumer.schema.recommendation import RecommendMessage
from storage.rabbit import channel_pool

async def handle_get_recommends(message: RecommendMessage):
    if message['action'] == 'get_recommends':
        recommendations = chroma_manager.get_recommends_by_id(message)        
        async with channel_pool.acquire() as channel:
            exchange = await channel.declare_exchange("user_recommendations", ExchangeType.DIRECT, durable=True)

            for recommendation in recommendations:
                await exchange.publish(
                    aio_pika.Message(
                        msgpack.packb(recommendation),
                    ),
                    routing_key=settings.USER_RECOMMENDATIONS_QUEUE_TEMPLATE.format(user_id=message['user_id']),
                )
