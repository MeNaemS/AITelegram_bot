from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message
from config import settings
from services.requests import SendRequests
from services.api_integration import chat
import asyncio

bot: AsyncTeleBot = AsyncTeleBot(settings.bot.token)
request: SendRequests = SendRequests(settings.api.host, settings.api.port, settings.bot.login, settings.bot.password)


async def send_typing_action(chat_id):
    while True:
        await bot.send_chat_action(chat_id, 'typing')
        await asyncio.sleep(4)


@bot.message_handler(func=lambda message: True)
async def handle_message(message: Message) -> None:
    typing_task = asyncio.create_task(send_typing_action(message.chat.id))
    try:
        response: str = await chat(request, message)
        await bot.send_message(message.chat.id, response)
    finally:
        typing_task.cancel()
        try:
            await typing_task
        except asyncio.CancelledError:
            pass
