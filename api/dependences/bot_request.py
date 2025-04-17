from typing import Annotated, Union, List
from fastapi import Depends, Request
from models.user_data import UserInDB
from models.integration import ClientTextMessage, ClientImageMessage, TelegramParameters, Response, ChatParameters, Model
from .auth import current_user
from services.bot_integration import service_ask_bot


async def depends_ask_bot(
    request: Request,
    user: Annotated[UserInDB, Depends(current_user)],
    model: Model,
    message_data: Union[ClientTextMessage, ClientImageMessage],
    telegram_parameters: TelegramParameters,
    chat_parameters: ChatParameters
) -> Response:
    return await service_ask_bot(
        user,
        request.state.db_connection,
        request.state.session,
        model,
        message_data,
        telegram_parameters,
        chat_parameters
    )
