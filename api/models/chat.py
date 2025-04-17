from typing import List, Optional
from pydantic import BaseModel


class Message(BaseModel):
    text_content: Optional[str]
    image_content: Optional[str]
    is_bot_message: bool


class ChatInfo(BaseModel):
    chat_id: int
    messages: List[Message]
