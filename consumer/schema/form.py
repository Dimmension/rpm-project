from .base import BaseMessage


class FormMessage(BaseMessage):
    action: str
    user_id: int
    user_tag: str
    photo: str
    username: str
    age: int
    gender: str
    city: str
    description: str | None
    filter_by_gender: str
    filter_by_age_min: int | None
    filter_by_age_max: int | None
    filter_by_description: str | None


class DeleteFormMessage(BaseMessage):
    action: str
    user_id: int
