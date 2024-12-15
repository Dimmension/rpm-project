from .base import BaseMessage


class RecommendMessage(BaseMessage):
    action: str
    user_id: int