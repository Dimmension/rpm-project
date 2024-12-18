from consumer.schema.form import FormMessage
from storage.db import driver
from models.encoder import get_embeddings
from storage.queries import INSERT_USER, CHANGE_USER


async def get_user_data(message: FormMessage) -> dict[str, str | int | list[float] | None]:
    user_data = {
        field: field_data
        for field, field_data in message.items()
        if field not in {'action', 'event'}
    }

    user_data['description_embedding'] = get_embeddings(
        user_data['description'],
    )
    user_data['filter_by_description_embedding'] = get_embeddings(
        user_data['filter_by_description'],
    )
    return user_data


async def handle_event_form(message: FormMessage):
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
