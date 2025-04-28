"""This module contains the lifespan for the application."""
# Importing the contextlib module
from contextlib import asynccontextmanager

# Importing the fastapi module
from fastapi import FastAPI

# Importing the ollama module, database connection, config, and logging
from ollama import AsyncClient
from database.connect import create_connection, PGConnection
from config import settings
from logging import getLogger, Logger

#		-- Creating the logger --
logger: Logger = getLogger(__name__)


#		    -- Lifespan --
@asynccontextmanager
async def lifespan(app: FastAPI):
    connection: PGConnection = await create_connection(settings.api.db)
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
