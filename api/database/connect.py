from typing import Sequence, Any, Tuple, Awaitable, List, Optional
import asyncpg
from schemas.settings import DB


class PGConnection:
    def __init__(self, connection: asyncpg.Connection):
        self.__connection: asyncpg.Connection = connection

    @property
    def connection(self) -> asyncpg.Connection:
        return self.__connection

    async def execute(self, query: str, *args: Tuple[Any]) -> Awaitable[str]:
        return await self.__connection.execute(query, *args)

    async def executemany(self, command: str, args: Sequence[Any]) -> None:
        return await self.__connection.executemany(command, args)

    async def fetch(self, query: str, *args: Tuple[Any]) -> Awaitable[List[asyncpg.Record]]:
        return await self.__connection.fetch(query, *args)

    async def fetchval(self, query: str, *args: Tuple[Any]) -> Awaitable[Any]:
        return await self.__connection.fetchval(query, *args)

    async def fetchrow(self, query: str, *args: Tuple[Any]) -> Awaitable[Optional[asyncpg.Record]]:
        return await self.__connection.fetchrow(query, *args)

    async def close(self):
        await self.__connection.close()


async def create_connection(db: DB) -> PGConnection:
    connection: PGConnection = PGConnection(
        await asyncpg.connect(
            host=db.host, port=db.port,
            user=db.username, password=db.password,
            database=db.database
        )
    )
    with open('./migrations/base_migration.sql', 'r') as migration:
        await connection.execute(migration.read())
    return connection
