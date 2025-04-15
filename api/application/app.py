from fastapi import FastAPI, status
from fastapi.responses import ORJSONResponse
import asyncpg
from dependences import lifespan
from router import api_router, auth_router

app = FastAPI(lifespan=lifespan)

app.include_router(api_router)
app.include_router(auth_router)

app.add_exception_handler(
    asyncpg.UniqueViolationError,
    lambda _, error: ORJSONResponse(
        {
            "message": "Resource already exists. The login is already taken."
        },
        status_code=status.HTTP_409_CONFLICT
    )
)

app.add_exception_handler(
    asyncpg.PostgresError,
    lambda _, error: ORJSONResponse(
        {
            "message": str(error)
        },
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
)
