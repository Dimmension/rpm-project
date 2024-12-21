# import uuid

# import aio_pika
# import msgpack
# import pytest
# from pathlib import Path

# from consumer.app import start_consumer
# from consumer.schema.recommendation import RecMessage
# from tests.mocking.rabbit import MockExchange
# from storage import queries, consts
# from storage.db import driver
# from neo4j import AsyncResult
# from storage.rabbit import channel_pool
# from aio_pika import ExchangeType

# BASE_DIR = Path(__file__).parent
# SEED_DIR = BASE_DIR / 'seeds'


# @pytest.mark.parametrize(
#     ('predefined_queue', 'seeds'),
#     [
#         (
#             RecMessage(event='user_recommendations', action='get_recommendations', user_id=1),
#             [SEED_DIR / 'public.user.json'],
#         ),
#     ]
# )
# @pytest.mark.asyncio()
# @pytest.mark.usefixtures('_load_queue', '_load_seeds')
# async def test_handle_gift(db_session, predefined_queue, mock_exchange: MockExchange) -> None:
#     await start_consumer()
#     expected_calls = []
#     # expected_routing_key = consts.USER_RECOMMENDATIONS_QUEUE_TEMPLATE.format(user_id=predefined_queue['user_id'])

#     # async with db_session:
#     #     not_fetched = await db_session.execute(select(Gift).order_by(func.random()))
#     #     tuple_rows = not_fetched.all()
#     #     gifts = [row for row, in tuple_rows]

#     #     for gift in gifts:
#     #         expected_message = aio_pika.Message(
#     #             msgpack.packb({
#     #                 'name': gift.name,
#     #                 'photo': gift.photo,
#     #                 'category': gift.category,
#     #             }),
#     #             correlation_id=correlation_id,
#     #         )
#     async with driver.session() as session:
#         results: AsyncResult = await session.run(
#             query=queries.GET_RECOMMENDATIONS,
#             parameters={'user_id': predefined_queue['user_id'], 'top_k': 10}
#         )
#         recommendations = await results.data()
#         async with channel_pool.acquire() as channel:
#             exchange = await channel.declare_exchange(
#                 consts.EXCHANGE_NAME,
#                 ExchangeType.DIRECT,
#                 durable=True,
#             )
#         for recommendation in recommendations:
#             recommendation['user_id'] = recommendation.pop('recommended_user_id')
#             expected_message = exchange.publish(
#                 aio_pika.Message(
#                     msgpack.packb(recommendation),
#                     priority=consts.BASE_PRIORITY,
#                 ),
#             )

#             expected_calls.append(
#                 ('publish', (expected_message,))
#             )

#     mock_exchange.assert_has_calls(expected_calls, any_order=True)
