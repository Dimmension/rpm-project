import aio_pika
from consumer.schema.form import DeleteFormMessage, FormMessage
from models.consts import DEFAULT_DESCRIPTION_EMBEDDING
from storage.db import driver
from models.encoder import get_embeddings
from storage.queries import INSERT_USER, CHANGE_USER, DELETE_USER
from storage.rabbit import channel_pool
from storage.consts import USER_RECOMMENDATIONS_QUEUE_TEMPLATE


async def get_user_data(message: FormMessage) -> dict[str, str | int | list[float] | None]:
    # user_data = message.model_dump(mode='json', exclude={'action', 'event'})
    user_data = {
        field: field_data
        for field, field_data in message.items()
        if field not in {'action', 'event'}
    }
    user_data['description_embedding'] = get_embeddings(
        user_data['description'],
    )
    if user_data['description_embedding'] is None:
        user_data['description_embedding'] = DEFAULT_DESCRIPTION_EMBEDDING

    user_data['filter_by_description_embedding'] = get_embeddings(
        user_data['filter_by_description'],
    )
    return user_data


async def handle_event_form(message: FormMessage | DeleteFormMessage):
    if message['action'] == 'send_form':
        async with driver.session() as session:
            user_data = await get_user_data(message)
            await session.run(
                query=INSERT_USER,
                parameters=user_data,
            )

    elif message['action'] == 'change_form':
        async with driver.session() as session:
            user_data = await get_user_data(message)
            await session.run(
                query=CHANGE_USER,
                parameters=user_data,
            )

    elif message['action'] == 'delete_form':
        channel: aio_pika.Channel
        async with channel_pool.acquire() as channel:
            await channel.queue_delete(
                queue_name=USER_RECOMMENDATIONS_QUEUE_TEMPLATE.format(
                    user_id=message['user_id'],
                ),
            )

        async with driver.session() as session:
            await session.run(
                query=DELETE_USER,
                parameters={'user_id': message['user_id']},
            )