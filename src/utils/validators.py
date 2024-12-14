import re
import src.consts


def valid_username(username: str) -> str | None:
    if not username.isalpha():
        return 'Имя должно состоять из букв!'
    elif len(username) > src.consts.MAX_USERNAME_LENGTH:
        return f'Длина имени не должна превосходить: {src.consts.MAX_USERNAME_LENGTH}!'
    return None


def valid_age(age: str) -> str | None:
    if not bool(re.match(src.consts.AGE_REGEXP, age)):
        return 'Неправильный возраст!'
    return None


def valid_description(description: str) -> str | None:
    if len(description) > src.consts.MAX_DESCRIPTION_LENGTH:
        return f'Длина описания не должна первосходить: {src.consts.MAX_DESCRIPTION_LENGTH}'
    return None


def valid_filter_by_age(filter_by_age: str) -> str | None:
    if not bool(re.match(src.consts.FILTER_BY_AGE_REGEXP, filter_by_age)):
        return 'Неправильный формат (пример: 12-34)'

    age_lower_bound, age_upper_bound = filter_by_age.split('-')
    if int(age_lower_bound) > int(age_upper_bound):
        return 'Неправильный диапазон'

    return None


def valid_filter_by_description(filter_by_description: str) -> str | None:
    return valid_description(filter_by_description)
