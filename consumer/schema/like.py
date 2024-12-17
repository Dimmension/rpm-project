from .base import BaseMessage

class LikeMessage(BaseMessage):
    action: str
    user_id: int
    target_user_id: int