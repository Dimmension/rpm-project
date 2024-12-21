from .base import BaseMessage

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
