from contextlib import asynccontextmanager
from fastapi import FastAPI
from database.connect import create_connection, PGConnection
from services.http_connection import AioHttp
from config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    connection: PGConnection = await create_connection(settings.api.db)
    session: AioHttp = AioHttp(settings.api.openai.api_key)
    yield {
        "db_connection": connection,
        "http_session": session,
        "settings": settings
    }
    await connection.close()
    await session.close()
