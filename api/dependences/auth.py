from typing import Awaitable
from fastapi import Request, Header
from models.user_data import UserAuth, UserRegister, UserInDB
from services.auth import authorization, current_user as current_user_service


async def auth_login(request: Request, user_auth: UserAuth) -> Awaitable[str]:
    return await authorization(request.state.db_connection, request.state.settings.api.jwt, user_auth)


async def auth_register(request: Request, user_register: UserRegister) -> Awaitable[str]:
    return await authorization(
        request.state.db_connection,
        request.state.settings.api.jwt,
        user_register,
        is_register=True
    )


async def current_user(request: Request, token: str = Header(...)) -> Awaitable[UserInDB]:
    return await current_user_service(
        request.state.db_connection,
        token,
        request.state.settings.api.jwt
    )
