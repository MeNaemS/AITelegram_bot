from contextlib import asynccontextmanager
from fastapi import FastAPI
from ollama import AsyncClient
from database.connect import create_connection, PGConnection
from config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    connection: PGConnection = await create_connection(settings.api.db)
    session: AsyncClient = AsyncClient(host="http://localhost:11434")
    yield {
        "db_connection": connection,
        "session": session,
        "settings": settings
    }
    await connection.close()
