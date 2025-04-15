from typing import TypedDict, List, Optional


class Imageurl(TypedDict):
    url: str


class MessageContent(TypedDict):
    type: str
    text: Optional[str]
    image_url: Optional[Imageurl]


class UserContent(TypedDict):
    role: str
    content: List[MessageContent]


class AiRequest(TypedDict):
    model: str
    messages: List[UserContent]
