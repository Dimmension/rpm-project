from aiogram import F
from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
import msgpack

from consumer.schema.form import FormMessage
from src.handlers.states.auth import AuthGroup
from src.handlers.states.profile import EditProfileForm
from src.utils import validators
from storage import consts
from storage.db import driver
from storage.queries import GET_USER_DATA
from storage.rabbit import send_msg
from .router import router


from src.handlers import buttons


@router.message(F.text == buttons.CHANGE_PROFILE_MSG)
async def change_profile(message: Message, state: FSMContext) -> None:
    await message.answer('Загрузка...', reply_markup=ReplyKeyboardRemove())

    async with driver.session() as session:
        result = await session.run(
            query=GET_USER_DATA,
            parameters={'user_id': message.from_user.id},
        )
        user_data = (await result.data())[0]

    age_min = user_data.pop('filter_by_age_min')
    age_max = user_data.pop('filter_by_age_max')

    if not age_min:
        filter_by_age = None
    else:
        filter_by_age = f'{age_min}-{age_max}'

    user_data['filter_by_age'] = filter_by_age
    await state.update_data(**user_data)
    await state.set_state(EditProfileForm.username)

    markup = InlineKeyboardMarkup(
        inline_keyboard=[[buttons.no_changes]]
    )
    await message.answer(
        f'Текущее имя: {await state.get_value('username')}',
        reply_markup=markup,
    )


@router.callback_query(
    F.data == buttons.NO_CHANGES_CALLBACK_MSG,
    EditProfileForm.username,
)
async def capture_username_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await _process_username(callback.message, state)


@router.message(EditProfileForm.username)
async def capture_username(message: Message, state: FSMContext) -> None:
    valid_msg = validators.valid_username(message.text)
    if valid_msg:
        await message.answer(valid_msg)
        return

    await state.update_data(username=message.text)
    await _process_username(message, state)


async def _process_username(message: Message, state: FSMContext) -> None:
    await state.set_state(EditProfileForm.age)

    markup = InlineKeyboardMarkup(
        inline_keyboard=[[buttons.no_changes]]
    )
    await message.answer(
        f'Текущий возраст: {await state.get_value('age')}',
        reply_markup=markup,
    )


@router.callback_query(
    F.data == buttons.NO_CHANGES_CALLBACK_MSG,
    EditProfileForm.age,
)
async def capture_age_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await _process_age(callback.message, state)


@router.message(EditProfileForm.age)
async def capture_age(message: Message, state: FSMContext) -> None:
    valid_msg = validators.valid_age(message.text)
    if valid_msg:
        await message.answer(valid_msg)
        return

    await state.update_data(age=message.text)
    await _process_age(message, state)


async def _process_age(message: Message, state: FSMContext) -> None:
    await state.set_state(EditProfileForm.gender)

    user_gender = await state.get_value('gender')

    if user_gender == buttons.MASCULINE_CALLBACK_MSG:
        remaining_choice = buttons.feminine
        user_gender = buttons.MASCULINE_MSG
    else:
        remaining_choice = buttons.masculine
        user_gender = buttons.FEMININE_MSG

    markup = InlineKeyboardMarkup(
        inline_keyboard=[[buttons.no_changes, remaining_choice]],
    )
    await message.answer(
        f'Текущий пол: {user_gender}',
        reply_markup=markup,
    )


@router.callback_query(
    F.data == buttons.NO_CHANGES_CALLBACK_MSG,
    EditProfileForm.gender,
)
async def capture_gender_no_changes_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await _process_gender(callback.message, state)


@router.callback_query(
    F.data.in_({buttons.FEMININE_CALLBACK_MSG, buttons.MASCULINE_CALLBACK_MSG}),
    EditProfileForm.gender,
)
async def capture_gender_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(gender=callback.data)
    await _process_gender(callback.message, state)


async def _process_gender(message: Message, state: FSMContext) -> None:
    await state.set_state(EditProfileForm.description)

    user_description = await state.get_value('description')

    if user_description:
        markup = InlineKeyboardMarkup(
            inline_keyboard=[[buttons.no_changes, buttons.drop_value]]
        )
    else:
        markup = InlineKeyboardMarkup(
            inline_keyboard=[[buttons.no_changes]],
        )

    if user_description:
        text = f'Текущее описание: {user_description}.'
    else:
        text = 'Вы не указали описание.'

    await message.answer(
        text,
        reply_markup=markup,
    )


@router.callback_query(
    F.data == buttons.NO_CHANGES_CALLBACK_MSG,
    EditProfileForm.description,
)
async def capture_description_no_changes_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await _process_description(callback.message, state)


@router.callback_query(
    F.data == buttons.DROP_VALUE_CALLBACK_MSG,
    EditProfileForm.description,
)
async def capture_drop_description(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(description=None)
    await _process_description(callback.message, state)


@router.message(EditProfileForm.description)
async def capture_description(message: Message, state: FSMContext) -> None:
    valid_msg = validators.valid_description(message.text)
    if valid_msg:
        await message.answer(valid_msg)
        return
    await state.update_data(description=message.text)
    await _process_description(message, state)


async def _process_description(message: Message, state: FSMContext) -> None:
    await state.set_state(EditProfileForm.filter_by_age)

    user_filter_by_age = await state.get_value('filter_by_age')

    if user_filter_by_age:
        markup = InlineKeyboardMarkup(
            inline_keyboard=[[buttons.no_changes, buttons.drop_value]],
        )
    else:
        markup = InlineKeyboardMarkup(
            inline_keyboard=[[buttons.no_changes]],
        )

    if user_filter_by_age:
        text = f'Текущий фильтр по возрасту: {user_filter_by_age}'
    else:
        text = 'Вы не указали фильтр по возрасту.'

    await message.answer(
        text,
        reply_markup=markup,
    )


@router.callback_query(
    F.data == buttons.NO_CHANGES_CALLBACK_MSG,
    EditProfileForm.filter_by_age,
)
async def capture_filter_by_age_no_changes_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await _process_filter_by_age(callback.message, state)


@router.callback_query(
    F.data == buttons.DROP_VALUE_CALLBACK_MSG,
    EditProfileForm.filter_by_age,
)
async def capture_drop_filter_by_age(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(filter_by_age=None)
    await _process_filter_by_age(callback.message, state)


@router.message(EditProfileForm.filter_by_age)
async def capture_filter_by_age(message: Message, state: FSMContext) -> None:
    valid_msg = validators.valid_filter_by_age(message.text)
    if valid_msg:
        await message.answer(valid_msg)
        return
    await state.update_data(filter_by_age=message.text)
    await _process_filter_by_age(message, state)


async def _process_filter_by_age(message: Message, state: FSMContext) -> None:
    await state.set_state(EditProfileForm.filter_by_gender)

    user_filter_by_gender = await state.get_value('filter_by_gender')

    if user_filter_by_gender == buttons.MASCULINE_CALLBACK_MSG:
        remaining_buttons = [buttons.feminine, buttons.no_preferences]
        user_filter_by_gender = buttons.MASCULINE_MSG

    elif user_filter_by_gender == buttons.FEMININE_CALLBACK_MSG:
        remaining_buttons = [buttons.masculine, buttons.no_preferences]
        user_filter_by_gender = buttons.FEMININE_MSG

    else:
        remaining_buttons = [buttons.masculine, buttons.feminine]
        user_filter_by_gender = buttons.NO_PREFERENCES_MSG

    markup = InlineKeyboardMarkup(
        inline_keyboard=[[buttons.no_changes, *remaining_buttons]],
    )

    await message.answer(
        f'Текущий фильтр по полу: {user_filter_by_gender}',
        reply_markup=markup,
    )


@router.callback_query(
    F.data == buttons.NO_CHANGES_CALLBACK_MSG,
    EditProfileForm.filter_by_gender,
)
async def capture_filter_by_gender_no_changes_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await _process_filter_by_gender(callback.message, state)


@router.callback_query(
    F.data.in_({
        buttons.FEMININE_CALLBACK_MSG,
        buttons.MASCULINE_CALLBACK_MSG,
        buttons.NO_PREFERENCES_CALLBACK_MSG,
    }),
    EditProfileForm.filter_by_gender,
)
async def capture_filter_by_gender_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(filter_by_gender=callback.data)
    await _process_filter_by_gender(callback.message, state)


async def _process_filter_by_gender(message: Message, state: FSMContext) -> None:
    await state.set_state(EditProfileForm.filter_by_description)

    user_filter_by_description = await state.get_value('filter_by_description')

    if user_filter_by_description:
        markup = InlineKeyboardMarkup(
            inline_keyboard=[[buttons.no_changes, buttons.drop_value]]
        )
    else:
        markup = InlineKeyboardMarkup(
            inline_keyboard=[[buttons.no_changes]],
        )

    if user_filter_by_description:
        text = f'Текущий фильтр по описанию: {user_filter_by_description}.'
    else:
        text = 'Вы не указали фильтр по описанию.'

    await message.answer(
        text,
        reply_markup=markup,
    )


@router.callback_query(
    F.data == buttons.NO_CHANGES_CALLBACK_MSG,
    EditProfileForm.filter_by_description,
)
async def capture_filter_by_description_no_changes_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await _process_filter_by_description(callback.message, state)


@router.callback_query(
    F.data == buttons.DROP_VALUE_CALLBACK_MSG,
    EditProfileForm.filter_by_description,
)
async def capture_drop_filter_by_description(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(filter_by_description=None)
    await _process_filter_by_description(callback.message, state)


@router.message(EditProfileForm.filter_by_description)
async def capture_filter_by_description(message: Message, state: FSMContext) -> None:
    valid_msg = validators.valid_filter_by_description(message.text)
    if valid_msg:
        await message.answer(valid_msg)
        return
    await state.update_data(filter_by_description=message.text)
    await _process_filter_by_description(message, state)


async def _process_filter_by_description(message: Message, state: FSMContext) -> None:
    form: dict[str, str | int] = {
        field: field_data
        for field, field_data in (await state.get_data()).items()
    }
    form['age'] = int(form['age'])

    filter_by_age_field = form.pop('filter_by_age')
    if filter_by_age_field:
        age_min, age_max = map(int, filter_by_age_field.split('-'))
    else:
        age_min = age_max = None

    form['filter_by_age_min'] = age_min
    form['filter_by_age_max'] = age_max

    await state.set_state(AuthGroup.authorized)
    await send_msg(
        consts.EXCHANGE_NAME,
        consts.GENERAL_USERS_QUEUE_NAME,
        [
            msgpack.packb(
                FormMessage(
                    event='user_form',
                    action='change_form',
                    **form,
                ),
            ),
        ],
    )
    markup = ReplyKeyboardMarkup(
        keyboard=[[buttons.settings]],
    )
    await message.answer(
        'Ваши изменения успешно применены!',
        reply_markup=markup,
    )
