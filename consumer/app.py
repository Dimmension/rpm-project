import msgpack
from consumer.handlers.form import handle_event_form
from consumer.handlers.like import handle_event_like
from consumer.handlers.recommendation import handle_event_recommendations
from storage.rabbit import channel_pool


async def start_consumer() -> None:
    queue_name = 'user_messages'
    async with channel_pool.acquire() as channel:
        await channel.set_qos(prefetch_count=10)
        print(channel)
        queue = await channel.declare_queue(queue_name, durable=True)
        print(queue)
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    body = msgpack.unpackb(message.body)
                    if body['event'] == 'user_form':
                        await handle_event_form(body)
                    elif body['event'] == 'user_recommendations':
                        await handle_event_recommendations(body)
                    elif body['event'] == 'like':
                        await handle_event_like(body)
