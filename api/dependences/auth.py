from fastapi import Request
from models.user_data import UserAuth, UserRegister
from services.auth import authorization


async def auth_login(request: Request, user_auth: UserAuth):
    return await authorization(request.state.db_connection, request.state.settings.api.jwt, user_auth)


async def auth_register(request: Request, user_register: UserRegister):
    return await authorization(
        request.state.db_connection,
        request.state.settings.api.jwt,
        user_register,
        is_register=True
    )
