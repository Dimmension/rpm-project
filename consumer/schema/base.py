# from pydantic import BaseModel
from typing import TypedDict


class BaseMessage(TypedDict):
    event: str
