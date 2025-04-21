from typing import TypedDict, Optional, List


class AuthResponse(TypedDict):
    access_token: str
    token_type: str
    expires_delta: str


class Message(TypedDict):
    role: str
    content: str
    images: Optional[List[str]]
    tool_calls: Optional[List[str]]


class AIResponse(TypedDict):
    model: str
    created_at: str
    done: bool
    done_reason: str
    total_duration: int
    loading_duration: int
    prompt_eval_count: int
    prompt_eval_duration: int
    eval_count: int
    eval_duration: int
    message: Message
