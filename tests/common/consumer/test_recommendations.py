import aio_pika
import msgpack
from neo4j import AsyncResult
import pytest
from pathlib import Path

from consumer.schema.recommendation import RecMessage

from consumer.app import start_consumer
from tests.mocking.rabbit import MockExchange

from storage.consts import USER_RECOMMENDATIONS_QUEUE_TEMPLATE, BASE_PRIORITY
from storage.queries import GET_RECOMMENDATIONS

BASE_DIR = Path(__file__).parent
SEED_DIR = BASE_DIR / 'seeds'


@pytest.mark.parametrize(
    ('predefined_queue', 'seeds'),
    [
        (
            RecMessage(
                event='user_recommendations',
                action='get_recommendations',
                user_id=1,
            ),
            [SEED_DIR / 'users.json'],
        ),
    ]
)
@pytest.mark.asyncio
@pytest.mark.usefixtures('_load_queue', '_load_seeds')
async def test_handle_recommendations(db_session, predefined_queue, mock_exchange: MockExchange) -> None:
    await start_consumer()
    expected_routing_key = USER_RECOMMENDATIONS_QUEUE_TEMPLATE.format(
        user_id=predefined_queue['user_id'],
    )

    expected_calls = []
    results: AsyncResult = await db_session.run(
        query=GET_RECOMMENDATIONS,
        parameters={'user_id': predefined_queue['user_id'], 'top_k': 10},
    )
    recommendations = await results.data()

    for recommendation in recommendations:
        recommendation['user_id'] = recommendation.pop('recommended_user_id')
        expected_message = aio_pika.Message(
            msgpack.packb(recommendation),
            priority=BASE_PRIORITY,
        )

        expected_calls.append(
            ('publish', (expected_message,), {'routing_key': expected_routing_key})
        )

    mock_exchange.assert_has_calls(expected_calls)
