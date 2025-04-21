from typing import List, Optional
from fastapi import HTTPException
from models.user_data import UserInDB
from models.integration import ClientMessage, ChatParameters, TelegramParameters, Model
from models.chat import Message, ChatInfo
from schemas.db import DBChatInfo, DBFilteredMessages
from database.connect import PGConnection
from ollama import AsyncClient, ChatResponse, ResponseError
import logging

logger = logging.getLogger(__name__)

# Максимальное количество сообщений, которые будут храниться в истории чата
MAX_CHAT_HISTORY = 18


async def trim_chat_history(db_connection: PGConnection, chat_id: int, max_messages: int = MAX_CHAT_HISTORY):
    try:
        total_messages = await db_connection.fetchval(
            "SELECT COUNT(*) FROM Messages WHERE chat_id = $1",
            chat_id
        )
        if total_messages <= max_messages:
            return
        to_delete = total_messages - max_messages
        old_message_ids = await db_connection.fetch(
            """
            SELECT id FROM Messages WHERE chat_id = $1 
            ORDER BY created_at ASC LIMIT $2
            """,
            chat_id, to_delete
        )
        if not old_message_ids:
            return
        ids_to_delete = [row['id'] for row in old_message_ids]
        await db_connection.execute(
            """DELETE FROM Messages WHERE id = ANY($1::bigint[])""",
            ids_to_delete
        )
        logger.info(f"Trimmed chat {chat_id} history: removed {len(ids_to_delete)} old messages")
    except Exception as e:
        logger.error(f"Error trimming chat history: {str(e)}")


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
    messages: List[DBFilteredMessages] = await db_connection.fetch(
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
    await trim_chat_history(db_connection, chat_id)


async def check_model_available(session: AsyncClient, model_name: str) -> bool:
    """Check if a model exists and is ready to use."""
    try:
        models = await session.list()
        available_models = [model.name for model in models.models]
        if model_name in available_models:
            return True
        await session.show(model=model_name)
        return False
    except ResponseError as e:
        if "not found" in str(e).lower() or "404" in str(e):
            return False
        raise
    except Exception as e:
        logger.error(f"Error checking model availability: {str(e)}")
        return False


async def service_ask_bot(
    user: UserInDB,
    db_connection: PGConnection,
    session: AsyncClient,
    model: Model,
    messages_data: ClientMessage,
    telegram_parameters: TelegramParameters,
    chat_parameters: ChatParameters,
    ai_models: List[str]
) -> ChatResponse:
    if model.name not in ai_models:
        error_message = f"Model {model.name} not in allowed models list: {ai_models}"
        logger.warning(error_message)
        raise HTTPException(status_code=404, detail={"error": error_message})
    chat_info: ChatInfo = await get_user_chat(
        user, telegram_parameters, chat_parameters, db_connection
    )
    if messages_data.content:
        await save_message(
            db_connection,
            chat_info.chat_id,
            messages_data.content,
            False,
            user.id,
            False
        )
    
    for image_url in messages_data.images:
        await save_message(
            db_connection,
            chat_info.chat_id,
            image_url,
            True,
            user.id,
            False
        )
    try:
        response: ChatResponse = await session.chat(
            model=model.name,
            messages=[
                {
                    'role': 'system',
                    'content': """
                        Ты - полезный и дружелюбный ассистент, который всегда отвечает пользователям на русском языке.
                        Правила общения:
                        - Всегда пиши ответы только на русском языке
                        - Общайся уважительно и вежливо
                        - Используй HTML теги для форматирования (<b></b> для жирного текста, <i></i> для курсива)
                        - Не используй Markdown или MarkdownV2 форматирование
                        - Давай полезные и информативные ответы
                        - Если не знаешь ответ, честно признайся в этом
                        - Старайся делать ответы краткими и по существу, всегда спрашивай в конце ответа, если нужно что-то уточнить
                    """
                }
            ] + [
                {
                    'role': 'assistant' if message.is_bot_message else 'user',
                    'content': message.text_content if message.text_content else '',
                    'images': [message.image_content] if message.image_content else []
                } for message in chat_info.messages
            ] + [{'role': 'user'} | messages_data.model_dump()],
            options={
                'temperature': chat_parameters.temperature,
                'top_p': chat_parameters.top_p
            }
        )
        await save_message(
            db_connection,
            chat_info.chat_id,
            response.message.content,
            False,
            None,
            True
        )
        return response
    except ResponseError as e:
        error_message = f"Ollama API error: {str(e)}"
        status_code = 500
        if "404" in str(e) or "not found" in str(e).lower():
            error_message = f"Model {model.name} not found or not loaded: {str(e)}"
            status_code = 404
        elif "memory" in str(e).lower():
            error_message = f"Insufficient memory to run model {model.name}: {str(e)}"
            status_code = 507
        logger.error(error_message)
        await save_message(
            db_connection,
            chat_info.chat_id,
            f"Error: {error_message}",
            False,
            None,
            True
        )
        if status_code in [404, 507]:
            try:
                models = await session.list()
                available_models = [model.name for model in models.models]
                if available_models:
                    suggestion = f"Available models: {', '.join(available_models)}"
                    logger.info(suggestion)
                    await save_message(
                        db_connection,
                        chat_info.chat_id,
                        suggestion,
                        False,
                        None,
                        True
                    )
            except Exception as list_error:
                logger.error(f"Could not list available models: {str(list_error)}")
        raise HTTPException(status_code=status_code, detail={"error": error_message})
    except Exception as e:
        error_message = f"Unexpected error: {str(e)}"
        logger.error(error_message)
        await save_message(
            db_connection,
            chat_info.chat_id,
            f"Error: {error_message}",
            False,
            None,
            True
        )
        raise HTTPException(status_code=500, detail={"error": error_message})
