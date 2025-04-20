from typing import Optional, List
from pydantic import BaseModel


class Message(BaseModel):
    text_content: Optional[str] = None
    image_content: Optional[str] = None
    is_bot_message: bool


class ChatInfo(BaseModel):
    chat_id: int
    messages: List[Message]
