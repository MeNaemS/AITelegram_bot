from typing import List
from pydantic import BaseModel


class ModelParameters(BaseModel):
    model: str


class ImageUrl(BaseModel):
    url: str


class ClientTypeMessage(BaseModel):
    type: str


class ClientTextMessage(ClientTypeMessage):
    text: str


class ClientImageMessage(ClientTypeMessage):
    image_url: ImageUrl


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


class Response(BaseModel):
    response: str
