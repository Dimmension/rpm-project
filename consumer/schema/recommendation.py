from .base import BaseMessage


class RecMessage(BaseMessage):
    action: str
    user_id: int
