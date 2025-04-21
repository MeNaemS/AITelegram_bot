import asyncio
import functools
from typing import Callable, Any, Coroutine


def with_typing(bot, chat_id_arg: str = 'message'):
    def decorator(func: Callable[..., Coroutine[Any, Any, Any]]):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            chat_id = None
            if chat_id_arg in kwargs:
                obj = kwargs[chat_id_arg]
                chat_id = obj.chat.id if hasattr(obj, 'chat') else obj
            else:
                for arg in args:
                    if hasattr(arg, 'chat') and hasattr(arg.chat, 'id'):
                        chat_id = arg.chat.id
                        break
            if not chat_id:
                return await func(*args, **kwargs)
            async def send_typing():
                while True:
                    await bot.send_chat_action(chat_id, 'typing')
                    await asyncio.sleep(4)
            typing_task = asyncio.create_task(send_typing())
            try:
                return await func(*args, **kwargs)
            finally:
                typing_task.cancel()
                try:
                    await typing_task
                except asyncio.CancelledError:
                    pass
        
        return wrapper
    
    return decorator
