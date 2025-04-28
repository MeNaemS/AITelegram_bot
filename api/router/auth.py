"""This module contains the authentication endpoints for the API."""
# Importing the fastapi module
from fastapi import APIRouter, Depends

# Importing the Annotated type
from typing import Annotated

# Importing the token model and authentication dependencies
from dependences.auth import auth_login, auth_register
from models.verify import Token

#		-- Creating the authentication router --
router: APIRouter = APIRouter(prefix="/auth", tags=["auth"])


#			-- Authentication endpoints --
@router.post("/login", response_model=Token)
async def login(token: Annotated[Token, Depends(auth_login)]) -> Token:
	"""Login endpoint."""
	return token


@router.post("/register", response_model=Token)
async def register(token: Annotated[Token, Depends(auth_register)]) -> Token:
	"""Register endpoint."""
	return token
