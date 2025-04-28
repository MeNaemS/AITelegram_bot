from typing import Annotated, Optional
from fastapi import Depends, Request
from ollama import ChatResponse
from models.user_data import UserInDB
from models.integration import ClientMessage, TelegramParameters, ChatParameters, Model
from .auth import current_user
from services.bot_integration import service_ask_bot


async def depends_ask_bot(
    request: Request,
    user: Annotated[UserInDB, Depends(current_user)],
    message_data: ClientMessage,
    telegram_parameters: TelegramParameters,
    model: Optional[Model] = None,
    chat_parameters: Optional[ChatParameters] = None
) -> ChatResponse:
    return await service_ask_bot(
        user,
        request.state.db_connection,
        request.state.session,
        message_data,
        telegram_parameters,
        chat_parameters,
        request.state.settings.api.ai.models,
        model
    )
