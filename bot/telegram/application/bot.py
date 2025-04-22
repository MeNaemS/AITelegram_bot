from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message
from config import settings
from services.requests import SendRequests
from services.api_integration import chat
from services.decorators import with_typing
from services.utils import split_long_message

bot: AsyncTeleBot = AsyncTeleBot(settings.bot.token)
request: SendRequests = SendRequests(settings.api.host, settings.api.port, settings.bot.login, settings.bot.password)


@bot.message_handler(func=lambda message: True)
@with_typing(bot)
async def handle_message(message: Message) -> None:
    response: str = await chat(request, message)
    message_parts = await split_long_message(response)
    await bot.send_message(
        chat_id=message.chat.id,
        text=message_parts[0],
        parse_mode="HTML",
        reply_to_message_id=message.message_id
    )
    for part in message_parts[1:]:
        await bot.send_message(
            chat_id=message.chat.id,
            text=part,
            parse_mode="HTML"
        )
