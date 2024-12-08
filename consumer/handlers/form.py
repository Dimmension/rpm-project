import aio_pika
import msgpack
import logging
from consumer.schema.form import FormMessage, RecommendMessage
from consumer.storage.rabbit import channel_pool
from aio_pika import ExchangeType
from config.settings import settings
from consumer.recommend_system.chroma import chroma_manager
from faker import Faker
import random

faker = Faker()

def handle_event_form(message: FormMessage):
    if message['action'] == 'send_form':
        for i in range(10):
            fake = {
                'event': 'user_form', 
                'action': 'send_form',
                'user_id': i,
                'name': faker.name(),
                'age': random.randint(18, 80),
                'gender': random.choice(['мужчина', 'женщина']),
                'description': faker.text(max_nb_chars=200),
                'filter_by_age': random.randint(18, 80),
                'filter_by_gender': faker.text(max_nb_chars=200),
                'filter_by_description': faker.text(max_nb_chars=200),
            }
            print(fake)
            chroma_manager.add_to_collection(fake)
        chroma_manager.add_to_collection(message)

async def handle_recommend_query(message: RecommendMessage):
    logging.info('Recommendations query is called!')
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
