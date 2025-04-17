from typing import TypedDict


class DBChatInfo(TypedDict):
    id: int
    name: str
    temperature: float
    top_p: float


class DBFilteredMessages(TypedDict):
    content: str
    is_bot_message: bool

