from typing import TypedDict, List, Optional, Any
from datetime import timedelta


class Message(TypedDict):
    role: str
    content: str
    refusal: Optional[str]
    reasoning: Optional[str]


class Choice(TypedDict):
    logprobs: Optional[Any]
    finish_reason: str
    native_finish_reason: str
    index: int
    message: Message


class Usage(TypedDict):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class AiResponseModel(TypedDict):
    id: str
    provider: str
    model: str
    object: str
    created: timedelta
    choices: List[Choice]
    usage: Usage
