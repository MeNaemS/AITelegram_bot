"""This module contains the health check endpoint for the API."""
# Importing the fastapi module
from fastapi import APIRouter, status, Request
from fastapi.responses import ORJSONResponse

# Importing the health model
from models.health import Health

#		-- Creating the health check router --
router: APIRouter = APIRouter(prefix="/health", tags=["health"])

#			-- Health check endpoint --
@router.get("", response_model=Health)
async def health_check(request: Request) -> Health:
	return ORJSONResponse(
		status_code=status.HTTP_200_OK,
		content={"status": "healthy"}
	)
