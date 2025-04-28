"""This module contains the API endpoints for the application."""
# Importing the fastapi module
from fastapi import APIRouter, Depends

# Importing the Annotated type
from typing import Annotated

# Importing the chat response model and bot request dependencies
from dependences.bot_request import depends_ask_bot
from ollama import ChatResponse

#		-- Creating the API router --
router: APIRouter = APIRouter(prefix="/api", tags=["api"])


#			-- API endpoints --
@router.post("/ask_bot", response_model=ChatResponse)
async def ask_bot(response: Annotated[ChatResponse, Depends(depends_ask_bot)]) -> ChatResponse:
	"""Ask the AI a question."""
	return response
