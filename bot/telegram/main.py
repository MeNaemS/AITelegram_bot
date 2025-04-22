import asyncio
from application.bot import bot, request


async def main():
    await bot.infinity_polling()
    await request.close()


if __name__ == "__main__":
    asyncio.run(main())
