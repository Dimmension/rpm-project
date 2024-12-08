import msgpack
from consumer.handlers.form import handle_event_form, handle_recommend_query
from consumer.storage.rabbit import channel_pool
from consumer.recommend_system.chroma import chroma_manager
from config.settings import settings


async def main() -> None:
    chroma_manager.initialize_client()
    chroma_manager.create_or_get_collection(settings.COLLECTION_NAME)

    queue_name = 'user_messages'
    async with channel_pool.acquire() as channel:
        await channel.set_qos(prefetch_count=10)

        queue = await channel.declare_queue(queue_name, durable=True)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    body = msgpack.unpackb(message.body)
                    if body['event'] == 'user_form':
                        handle_event_form(body)
                    if body['event'] == 'recommendations':
                        await handle_recommend_query(body)