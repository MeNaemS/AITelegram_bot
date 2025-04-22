from typing import TypedDict, List, Union


class Imageurl(TypedDict):
    url: str


class MessageType(TypedDict):
    type: str


class MessageText(TypedDict):
    text: str


class MessageImage(TypedDict):
    image_url: Imageurl


class UserContent(TypedDict):
    role: str
    content: List[Union[MessageText, MessageImage]]


class AiRequest(TypedDict):
    model: str
    messages: List[UserContent]
    temperature: float
