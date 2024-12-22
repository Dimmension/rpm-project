import uuid

import aio_pika
import msgpack
import pytest
from pathlib import Path


from consumer.app import start_consumer
from consumer.schema.recommendation import RecMessage
from tests.mocking.rabbit import MockExchange
from storage import consts, queries
from storage.db import driver

BASE_DIR = Path(__file__).parent
SEED_DIR = BASE_DIR / 'seeds'


@pytest.mark.parametrize(
    ('predefined_queue', 'seeds', 'correlation_id'),
    [
        (
            RecMessage(event='user_recommendation', action='get_recommendations', user_id=1),
            [SEED_DIR / 'public.user.json'],
            str(uuid.uuid4()),
        ),
    ]
)
@pytest.mark.asyncio()
@pytest.mark.usefixtures('_load_queue', '_load_seeds')
async def test_handle_gift(db_session, predefined_queue, correlation_id, mock_exchange: MockExchange) -> None:
    await start_consumer()
    expected_routing_key = consts.USER_RECOMMENDATIONS_QUEUE_TEMPLATE.format(user_id=predefined_queue['user_id'])
    expected_calls = []

    async with driver.session() as session:
        results = await session.run(
            query=queries.GET_RECOMMENDATIONS,
            parameters={'user_id': predefined_queue['user_id'], 'top_k': 10}
        )
        recommendations = await results.data()
        for recommendation in recommendations:
            recommendation['user_id'] = recommendation.pop('recommended_user_id')
            expected_message = aio_pika.Message(
                    msgpack.packb(recommendation),
                    priority=consts.BASE_PRIORITY,
            )
            expected_calls.append(
                ('publish', (expected_message,), {'routing_key': expected_routing_key})
            )
        mock_exchange.assert_has_calls(expected_calls, any_order=True)
