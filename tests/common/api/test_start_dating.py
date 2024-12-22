import pytest
from aiogram.types import User
from src.handlers.message.meet import show_recommendations
from tests.mocking.tg import MockTgMessage
from src.handlers.markups import recommendation
from unittest.mock import call
from src.templates.env import render

@pytest.mark.parametrize(
    ("predefined_queue",),
    [
        (
            {
                "action": "send_form",
                "user_id": "1",
                "user_tag": "dimmension",
                "photo": "aboba.jpg",
                "username": "Vadim",
                "age": "19",
                "gender": "masculine",
                "description": "I like Machine Learning",
                "filter_by_gender": "",
                "filter_by_age_min": "",
                "filter_by_age_max": "",
                "filter_by_description": ""
            },
        ),
        (None,)
    ]
)
@pytest.mark.asyncio
@pytest.mark.usefixtures('_load_queue')
async def test_start_gifting(predefined_queue):
    user = User(id=1, is_bot=False, is_premium=False, last_name='test', first_name='test')
    message = MockTgMessage(from_user=user)

    await show_recommendations(message, state=1)

    if predefined_queue:
        expected_text = render('user/user.jinja2', user=predefined_queue)

        message.assert_has_calls([
            call.answer_photo(
                None,
                caption=expected_text,
                reply_markup=recommendation
            )
        ])
    else:
        message.assert_has_calls([
            call.answer("Попробуйте позже или измените фильтры поиска.")
        ])
