from consumer.schema.form import FormMessage
from recsys.db import redis_manager
import logging.config
from consumer.logger import LOGGING_CONFIG, logger
logging.config.dictConfig(LOGGING_CONFIG)

async def handle_event_form(message: FormMessage):
    if message['action'] == 'send_form':
        try:
            redis_manager.add_to_collection(message)
            logger.info(f"User data added to Redis for user_id: {message['user_id']}")
        except Exception as error:
            logger.error(f"Failed to handle send_form: {error}")
