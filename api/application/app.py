from fastapi import FastAPI, status, Request
from fastapi.responses import ORJSONResponse
import asyncpg
from dependences import lifespan
from router import api_router, auth_router
import logging
import traceback

logger = logging.getLogger(__name__)

app = FastAPI(lifespan=lifespan)

app.include_router(api_router)
app.include_router(auth_router)

app.add_exception_handler(
    asyncpg.UniqueViolationError,
    lambda req, error: handle_exception(
        req,
        error,
        status.HTTP_409_CONFLICT,
        "Resource already exists."
    )
)
app.add_exception_handler(
    asyncpg.PostgresError,
    lambda req, error: handle_exception(req, error, status.HTTP_500_INTERNAL_SERVER_ERROR)
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return handle_exception(request, exc, status.HTTP_500_INTERNAL_SERVER_ERROR)


def handle_exception(request, error, status_code, custom_message=None):
    error_detail = {
        "path": request.url.path,
        "method": request.method,
        "error_type": error.__class__.__name__,
        "error": str(error)
    }
    logger.error(
        f"Error occurred: {error_detail['error_type']} - {error_detail['error']}\n"
        f"Path: {error_detail['path']}, Method: {error_detail['method']}\n"
        f"Traceback: {traceback.format_exc()}"
    )
    return ORJSONResponse(
        {
            "message": custom_message or str(error)
        },
        status_code=status_code
    )
