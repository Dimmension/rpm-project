import logging
from consumer.schema.form import FormMessage
from recsys.db import redis_manager

async def handle_event_form(message: FormMessage):
    if message['action'] == 'send_form':
        try:
            redis_manager.add_to_collection(message)
            logging.info(f"User data added to Redis for user_id: {message['user_id']}")
        except Exception as error:
            logging.error(f"Failed to handle send_form: {error}")
