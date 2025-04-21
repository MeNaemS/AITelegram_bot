from services.requests import SendRequests
from telebot.types import Message
from typing import Dict, Any


async def chat(request: SendRequests, message: Message) -> str:
    user_message: str = message.text
    if user_message == '/start':
        user_message = f'Привет, меня зовут {message.from_user.first_name}, а как тебя зовут?'
    try:
        response: Dict[str, Any] = await request.post(
            '/api/ask_bot',
            {
                'model': {
                    'name': 'llama3' if '@llama3' in user_message else 'qwen2.5'
                },
                'message_data': {
                    'content': user_message,
                },
                'telegram_parameters': {
                    'chat_id': str(message.chat.id)
                },
                'chat_parameters': {
                    'top_p': 0.9,
                    'temperature': 0.7,
                }
            }
        )
        return response['message']['content']
    except Exception as e:
        return f"<b>Извините, произошла ошибка:</b> {str(e)}"
