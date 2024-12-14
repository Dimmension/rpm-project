from sqlalchemy import insert

from model.user import User
from consumer.schema.form import FormMessage
from storage.db import async_session


async def handle_event_form(message: FormMessage):
    if message['action'] == 'send_form':
        async with async_session() as db:
            user_data = {
                field: field_data
                for field, field_data in message.items()
                if field not in {'user_id', 'action', 'event'}
            }
            user_data['id'] = message['user_id']

            await db.execute(insert(User).values(**user_data))
            await db.commit()

    elif message['action'] == 'change_form':
        pass
