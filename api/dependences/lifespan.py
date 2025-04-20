from contextlib import asynccontextmanager
from fastapi import FastAPI
from ollama import AsyncClient
from database.connect import create_connection, PGConnection
from config import settings
import logging

logging.config.fileConfig('logging_config.ini')
logger: logging.Logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    connection: PGConnection = await create_connection(settings.api.db)
    logger.info(
        f"Creating connection to ollama (http://{settings.api.ai.ollama_host}:{settings.api.ai.ollama_port})"
    )
    session: AsyncClient = AsyncClient(
        host=f"http://{settings.api.ai.ollama_host}:{settings.api.ai.ollama_port}"
    )
    logger.info("Session created")
    yield {
        "db_connection": connection,
        "session": session,
        "settings": settings
    }
    await connection.close()
