"""The main module of the application."""
# Importing the Optional type
from typing import Optional

# Importing the main FastAPI module
from fastapi import FastAPI, status, Request
from fastapi.responses import ORJSONResponse

# Importing the asyncpg module for error handling
from asyncpg import UniqueViolationError, PostgresError

# Importing the traceback module for error handling
import traceback

# Importing application lifecycle, existing routers, logging, and exception schemas
from router import api_router, auth_router, health_router
from schemas.exception import AppException
from logging import getLogger, Logger
from dependences import lifespan

#			-- Creating Basic Constants --
logger: Logger = getLogger(__name__)
app = FastAPI(lifespan=lifespan)

#		-- Including the routers in the application --
app.include_router(api_router)
app.include_router(auth_router)
app.include_router(health_router)

#			-- Adding an error handlers --
app.add_exception_handler(
	UniqueViolationError,
	lambda req, error: handle_exception(
		req,
		error,
		status.HTTP_409_CONFLICT,
		"Resource already exists."
	)
)
app.add_exception_handler(
	PostgresError,
	lambda req, error: handle_exception(req, error, status.HTTP_500_INTERNAL_SERVER_ERROR)
)


# Exception handler for unhandled exceptions
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> ORJSONResponse:
	return handle_exception(request, exc, status.HTTP_500_INTERNAL_SERVER_ERROR)


def handle_exception(
	request: Request,
	error: Exception,
	status_code: int,
	custom_message: Optional[str] = None
) -> ORJSONResponse:
	"""Main error handler for logging and displaying errors."""
	error_detail: AppException = {
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
		status_code=status_code,
		content={"message": custom_message or str(error)}
	)
