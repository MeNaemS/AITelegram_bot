from typing import Annotated, Union, List
from fastapi import Depends, Request
from models.user_data import UserInDB
from models.openrouterai.integration import ClientTextMessage, ClientImageMessage, TelegramParameters, ChatParameters, Response
from .auth import current_user
from services.bot_integration import service_ask_bot


async def depends_ask_bot(
    request: Request,
    user: Annotated[UserInDB, Depends(current_user)],
    message_data: List[Union[ClientTextMessage, ClientImageMessage]],
    telegram_parameters: TelegramParameters,
    chat_parameters: ChatParameters
) -> Response:
    return await service_ask_bot(
        user,
        request.state.db_connection,
        request.state.http_session,
        request.state.settings.api.openai,
        message_data,
        telegram_parameters,
        chat_parameters
    )
