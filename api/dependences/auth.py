"""This module contains the authentication dependencies for the application."""
# Importing the typing module
from typing import Awaitable

# Importing the fastapi module
from fastapi import Request, Header

# Importing the user data model, authorization service, current user service, and token model
from services.auth import authorization, current_user as current_user_service
from models.user_data import UserAuth, UserRegister, UserInDB
from models.verify import Token


#					-- Authentication dependencies --
async def auth_login(request: Request, user_auth: UserAuth) -> Awaitable[Token]:
	"""Login dependency."""
	return await authorization(
		request.state.db_connection,
		request.state.settings.api.jwt,
		user_auth
	)


async def auth_register(request: Request, user_register: UserRegister) -> Awaitable[Token]:
	"""Register dependency."""
	return await authorization(
		request.state.db_connection,
		request.state.settings.api.jwt,
		user_register,
		is_register=True
	)


async def current_user(request: Request, token: str = Header(...)) -> Awaitable[UserInDB]:
	"""Current user dependency."""
	return await current_user_service(
		request.state.db_connection,
		token,
		request.state.settings.api.jwt
	)
