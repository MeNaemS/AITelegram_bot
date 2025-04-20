from typing import List, Optional
from pydantic import BaseModel


class ModelParameters(BaseModel):
    model: str


class ClientMessage(BaseModel):
    content: Optional[str] = None
    images: List[str] = []


class TelegramParameters(BaseModel):
    chat_id: str


class Plugin(BaseModel):
    id: str
    max_results: int = 5
    search_prompt: str = "[nytimes.com](https://nytimes.com/some-page)"


class ChatParameters(BaseModel):
    top_p: float = 0.9
    temperature: float = 0.7
    plagins: List[Plugin] = []


class Model(BaseModel):
    name: str
