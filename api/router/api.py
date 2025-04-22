from typing import Annotated
from fastapi import APIRouter, Depends
from ollama import ChatResponse
from dependences.bot_request import depends_ask_bot

router: APIRouter = APIRouter(prefix="/api", tags=["api"])


@router.post("/ask_bot", response_model=ChatResponse)
async def ask_bot(response: Annotated[ChatResponse, Depends(depends_ask_bot)]) -> ChatResponse:
    return response
