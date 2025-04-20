from typing import Sequence, Any, Tuple, Awaitable, List, Optional
import asyncpg
from logging import Logger, getLogger
from schemas.settings import DB

logger: Logger = getLogger(__name__)


class PGConnection:
    def __init__(self, connection: asyncpg.Connection):
        self.__connection: asyncpg.Connection = connection

    @property
    def connection(self) -> asyncpg.Connection:
        return self.__connection

    async def execute(self, query: str, *args: Tuple[Any]) -> Awaitable[str]:
        logger.info(f"Executing query: {query}")
        return await self.__connection.execute(query, *args)

    async def executemany(self, command: str, args: Sequence[Any]) -> None:
        logger.info(f"Executing many query: {command}")
        return await self.__connection.executemany(command, args)

    async def fetch(self, query: str, *args: Tuple[Any]) -> Awaitable[List[asyncpg.Record]]:
        logger.info(f"Fetching query: {query}")
        return await self.__connection.fetch(query, *args)

    async def fetchval(self, query: str, *args: Tuple[Any]) -> Awaitable[Any]:
        logger.info(f"Fetching value query: {query}")
        return await self.__connection.fetchval(query, *args)

    async def fetchrow(self, query: str, *args: Tuple[Any]) -> Awaitable[Optional[asyncpg.Record]]:
        logger.info(f"Fetching row query: {query}")
        return await self.__connection.fetchrow(query, *args)

    async def close(self):
        logger.info("Closing connection")
        await self.__connection.close()


async def create_connection(db: DB) -> PGConnection:
    logger.info(f"Creating connection to {db.database} on {db.host}:{db.port}")
    connection: PGConnection = PGConnection(
        await asyncpg.connect(
            host=db.host, port=db.port,
            user=db.username, password=db.password,
            database=db.database
        )
    )
    logger.info("Executing base migration")
    with open('./migrations/base_migration.sql', 'r') as migration:
        await connection.execute(migration.read())
    logger.info("Base migration executed")
    return connection
