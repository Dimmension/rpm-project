from .base import BaseMessage


class LikeMessage(BaseMessage):
    action: str
    user_id: int
    other_id: int
    user_tag: str