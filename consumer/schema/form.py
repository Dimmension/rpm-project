from .base import BaseMessage


# TODO: event -> заполнение формы:
# actions:
# 1. Заполнить данные в первый раз
# 2. Изменить форму ? (подумать над реализацией)

class FormMessage(BaseMessage):
    action: str
    user_id: int
    photo: str
    username: str
    age: int
    gender: str
    description: str
    photo: str
    filter_by_age: str
    filter_by_gender: str
    filter_by_description: str
