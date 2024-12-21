
import aio_pika
import msgpack
import random
from aio_pika import ExchangeType
from faker import Faker

from config.settings import settings
from recsys.db import redis_manager
from consumer.schema.recommendation import RecMessage
from storage.rabbit import channel_pool, send_msg
from storage.consts import USER_RECOMMENDATIONS_QUEUE_TEMPLATE, EXCHANGE_NAME
import logging.config
from consumer.logger import LOGGING_CONFIG, logger
logging.config.dictConfig(LOGGING_CONFIG)

fake = Faker()

def add_fake_users(redis_manager, num_users=10):
    """
    Generate and add fake users to Redis using the Faker library.

    Args:
        redis_manager (RedisDBManager): The Redis manager instance.
        num_users (int): Number of fake users to add.
    """
    for _ in range(num_users):
        user_data = {
            "user_id": fake.uuid4(),
            "username": fake.user_name(),
            "age": random.randint(18, 60),
            "gender": random.choice(["Male", "Female", "Other"]),
            "description": fake.text(max_nb_chars=200),
            "filter_by_age": f"{random.randint(18, 60)}",
            "filter_by_gender": random.choice(["Male", "Female", "Any"]),
            "filter_by_description": fake.sentence(),
        }

        try:
            redis_manager.add_to_collection(user_data)
            logger.info(f"Fake user added: {user_data['username']}")
        except Exception as error:
            logger.error(f"Failed to add fake user: {error}")

async def handle_get_recommends(message: RecMessage):
    """
    Handles 'get_recommends' action, fetches recommendations from Redis, 
    and publishes them to RabbitMQ for the specified user.
    """
    if message['action'] == 'get_recommendations':
        add_fake_users(redis_manager, 10)
        recommendations = redis_manager.get_recommends_by_id(message['user_id'])
        for recommendation in recommendations:
            await send_msg(
                EXCHANGE_NAME, 
                USER_RECOMMENDATIONS_QUEUE_TEMPLATE.format(user_id=message['user_id']),
                [aio_pika.Message(body=msgpack.packb(recommendation))]
            )
            logger.info(f"Recommendations for user {message['user_id']} published successfully.")
