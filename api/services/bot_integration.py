from typing import Union, List, Optional
from models.user_data import UserInDB
from models.openrouterai.integration import ClientTextMessage, ClientImageMessage, TelegramParameters, ChatParameters, Response
from models.chat import Message, ChatInfo
from schemas.db import DBChatInfo, DBFilteredMessages
from schemas.openrouterai.response import AiResponseModel
from database.connect import PGConnection
from .http_connection import AioHttp
from schemas.settings import OpenAI


async def get_user_chat(
    user: UserInDB,
    telegram_parameters: TelegramParameters,
    chat_parameters: ChatParameters,
    db_connection: PGConnection,
) -> ChatInfo:
    chat: Optional[DBChatInfo] = await db_connection.fetchrow(
        """
        SELECT c.id, c.name, c.temperature, c.top_p FROM Chats c
        JOIN UserChats uc ON c.id = uc.chat_id WHERE uc.user_id = $1 AND c.name = $2
        """,
        user.id, telegram_parameters.chat_id
    )
    if not chat:
        chat_id: int = await db_connection.fetchval(
            "INSERT INTO Chats(name, temperature, top_p) VALUES ($1, $2, $3) RETURNING id",
            telegram_parameters.chat_id, chat_parameters.temperature, chat_parameters.top_p
        )
        await db_connection.execute(
            "INSERT INTO UserChats(user_id, chat_id, is_admin) VALUES ($1, $2, $3)",
            user.id, chat_id, True
        )
        chat: DBChatInfo = await db_connection.fetchrow(
            "SELECT id, name, temperature, top_p FROM Chats WHERE id = $1",
            chat_id
        )
    messages: DBFilteredMessages = await db_connection.fetch(
        """
        SELECT m.text_content, m.image_content, m.is_bot_message FROM Messages m
        LEFT JOIN Users u ON m.author_id = u.id WHERE m.chat_id = $1 ORDER BY m.created_at ASC
        """,
        chat['id']
    )
    return ChatInfo(
        chat_id=chat['id'],
        messages=[Message(**message) for message in messages]
    )


async def save_message(
    db_connection: PGConnection,
    chat_id: int,
    content: str,
    is_image: bool = False,
    author_id: Optional[int] = None,
    is_bot_message: bool = False
):
    await db_connection.execute(
        """
        INSERT INTO Messages({}, author_id, chat_id, is_bot_message
        )
        VALUES ($1, $2, $3, $4)
        """.format('text_content' if not is_image else 'image_content'),
        content, author_id, chat_id, is_bot_message
    )


async def service_ask_bot(
    user: UserInDB,
    db_connection: PGConnection,
    http_session: AioHttp,
    openai_settings: OpenAI,
    messages_data: List[Union[ClientTextMessage, ClientImageMessage]],
    telegram_parameters: TelegramParameters,
    chat_parameters: ChatParameters
) -> Response:
    chat_info: ChatInfo = await get_user_chat(
        user, telegram_parameters, chat_parameters, db_connection
    )
    for message in messages_data:
        await save_message(
            db_connection,
            chat_info.chat_id,
            message.text if isinstance(message, ClientTextMessage) else message.image_url.url,
            isinstance(message, ClientImageMessage),
            user.id,
            False
        )
    response: AiResponseModel = await http_session.post(
        url='chat/completions',
        json={
            'model': openai_settings.model,
            'messages': [
                {
                    'role': 'assistant' if message.is_bot_message else 'user',
                } | {
                    'content': message.text_content
                } if message.text_content is not None else {
                    'image_url': {
                        'url': message.image_content
                    }
                } for message in chat_info.messages
            ] + [
                {
                    'role': 'user',
                    'content': [message_data.model_dump() for message_data in messages_data]
                }
            ]
        } | chat_parameters.model_dump()
    )
    await save_message(
        db_connection,
        chat_info.chat_id,
        response['choices'][0]['message']['content'],
        False,
        None,
        True
    )
    return Response(response=response['choices'][0]['message']['content'])
