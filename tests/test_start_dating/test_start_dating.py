import pytest
from aiogram.types import User

from src.handlers.markups import recommendation
from src.handlers.message.meet import show_recommendations
from tests.mocking.tg import MockTgMessage


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "predefined_queue",
    [
        {
            "username": "Vadim",
            "age": "19",
            "gender": "masculine",
            "description": "I like Machine Learning",
        },
        None
    ]
)
@pytest.mark.usefixtures("_load_queue")
async def test_show_recommendations(predefined_queue):
    user = User(id=1, is_bot=False, is_premium=False, last_name='test', first_name='test')
    message = MockTgMessage(from_user=user)

    await show_recommendations(message, state=1)

    if predefined_queue:
        expected_text = (
            f"<b>Имя</b>: {predefined_queue['username']}\n"
            f"<b>Возраст</b>: {predefined_queue['age']}\n"
            f"<b>Пол</b>: {predefined_queue['gender']}\n"
            f"<b>Описание</b>: {predefined_queue['description']}"
        )
        message.assert_has_calls([
            ("answer", {"text": expected_text, "reply_markup": recommendation})
        ])
    else:
        message.assert_has_calls([
            ('answer', ('Попробуйте позже или измените фильтры поиска.',))
        ])
