from aiogram.types import InlineKeyboardButton

SKIP_MSG = 'Пропустить'
SKIP_CALLBACK_MSG = 'skip'

MASCULINE_MSG = 'Мужчина'
MASCULINE_CALLBACK_MSG = 'masculine'

FEMININE_MSG = 'Девушка'
FEMININE_CALLBACK_MSG = 'feminine'

NO_PREFERENCES_MSG = 'Все'
NO_PREFERENCES_CALLBACK_MSG = 'all'

AUTH_MSG = 'Авторизоваться'
AUTH_CALLBACK_MSG = '/auth'

masculine = InlineKeyboardButton(
    text=MASCULINE_MSG,
    callback_data=MASCULINE_CALLBACK_MSG,
)

feminine = InlineKeyboardButton(
    text=FEMININE_MSG,
    callback_data=FEMININE_CALLBACK_MSG,
)

no_preferences = InlineKeyboardButton(
    text=NO_PREFERENCES_MSG,
    callback_data=NO_PREFERENCES_CALLBACK_MSG,
)

skip = InlineKeyboardButton(
    text=SKIP_MSG,
    callback_data=SKIP_CALLBACK_MSG,
)

auth = InlineKeyboardButton(
    text=AUTH_MSG,
    callback_data=AUTH_CALLBACK_MSG,
)
