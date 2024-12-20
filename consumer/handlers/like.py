from consumer.bot import bot
from consumer.schema.like import LikeMessage

from storage.db import driver
from storage.queries import LIKE_USER


async def handle_event_like(message: LikeMessage) -> None:
    if message['action'] == 'put_like':
        user_id = message['user_id']
        other_id = message['other_id']
        user_tag = message['user_tag']

        await bot.send_message(
            chat_id=other_id,
            text=f'Матч: @{user_tag}',
        )
        async with driver.session() as session:
            await session.run(
                query=LIKE_USER,
                parameters={'user_id': user_id, 'other_id': other_id}
            )
