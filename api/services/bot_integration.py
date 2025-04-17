from typing import Union, List, Optional
from models.user_data import UserInDB
from models.integration import ClientTextMessage, ClientImageMessage, ChatParameters, TelegramParameters, Response, Model
from models.chat import Message, ChatInfo
from schemas.db import DBChatInfo, DBFilteredMessages
from database.connect import PGConnection
from ollama import AsyncClient, ChatResponse


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


async def service_ask_bot(
    user: UserInDB,
    db_connection: PGConnection,
    session: AsyncClient,
    model: Model,
    messages_data: Union[ClientTextMessage, ClientImageMessage],
    telegram_parameters: TelegramParameters,
    chat_parameters: ChatParameters
) -> Response:
    chat_info: ChatInfo = await get_user_chat(
        user, telegram_parameters, chat_parameters, db_connection
    )
    
    # Save the user message to the database
    await save_message(
        db_connection,
        chat_info.chat_id,
        messages_data.text if isinstance(messages_data, ClientTextMessage) else messages_data.image_url.url,
        isinstance(messages_data, ClientImageMessage),
        user.id,
        False
    )
    
    # Format messages for Ollama in the correct structure
    formatted_messages = []
    
    # Add chat history
    for message in chat_info.messages:
        if message.text_content is not None:
            formatted_messages.append({
                'role': 'assistant' if message.is_bot_message else 'user',
                'content': message.text_content
            })
        elif message.image_content is not None:
            # Handle image content if needed
            formatted_messages.append({
                'role': 'user',
                'content': f"[Image: {message.image_content}]"
            })
    
    # Add the current message
    if isinstance(messages_data, ClientTextMessage):
        formatted_messages.append({
            'role': 'user',
            'content': messages_data.text
        })
    else:
        # Handle image message
        formatted_messages.append({
            'role': 'user',
            'content': f"[Image URL: {messages_data.image_url.url}]"
        })
    
    try:
        # Make the API call with proper error handling
        response = await session.chat(
            model=model.name,
            messages=formatted_messages,
            options={
                'temperature': chat_parameters.temperature,
                'top_p': chat_parameters.top_p
            }
        )
        
        # Extract the response content
        response_content = response.message.content
        
        # Save the bot's response to the database
        await save_message(
            db_connection,
            chat_info.chat_id,
            response_content,
            False,
            None,
            True
        )
        
        return Response(response=response_content)
        
    except Exception as e:
        # Log the error and return a fallback response
        error_message = f"Error communicating with Ollama: {str(e)}"
        print(error_message)
        
        # Save the error message to the database
        await save_message(
            db_connection,
            chat_info.chat_id,
            f"Sorry, I encountered an error: {str(e)}",
            False,
            None,
            True
        )
        
        return Response(response=f"Sorry, I encountered an error: {str(e)}")
