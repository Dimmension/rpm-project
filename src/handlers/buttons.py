from aiogram.types import InlineKeyboardButton, KeyboardButton

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

NO_CHANGES_MSG = 'Не изменять'
NO_CHANGES_CALLBACK_MSG = '/no_changes'

DROP_VALUE_MSG = 'Сбросить'
DROP_VALUE_CALLBACK_MSG = '/drop_value'

SETTINGS_MSG = 'Настройки'
MEET_MSG = 'Найти знакомства'
CHANGE_PROFILE_MSG = 'Изменить профиль'
DELETE_PROFILE_MSG = 'Удалить профиль'
BACK_TO_MENU_MSG = 'Вернуться в меню'

LIKE_MSG = '🥰'
DISLIKE_MSG = '🫡'

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

settings = KeyboardButton(
    text=SETTINGS_MSG,
)

meet = KeyboardButton(
    text=MEET_MSG,
)

change_profile = KeyboardButton(
    text=CHANGE_PROFILE_MSG,
)

delete_profile = KeyboardButton(
    text=DELETE_PROFILE_MSG,
)

back_to_menu = KeyboardButton(
    text=BACK_TO_MENU_MSG,
)

no_changes = InlineKeyboardButton(
    text=NO_CHANGES_MSG,
    callback_data=NO_CHANGES_CALLBACK_MSG,
)

drop_value = InlineKeyboardButton(
    text=DROP_VALUE_MSG,
    callback_data=DROP_VALUE_CALLBACK_MSG,
)

like = KeyboardButton(
    text=LIKE_MSG,
)

dislike = KeyboardButton(
    text=DISLIKE_MSG,
)
