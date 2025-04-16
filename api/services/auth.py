"""
A service that performs token validation, encoding and decoding,
    and recording a new user in the database.
"""
from typing import Optional, Awaitable
from datetime import datetime, timedelta

# To display the status code related to authorization/authentication.
from fastapi import HTTPException, status

# To create a token and also hash the password.
from jwt import encode, decode
import jwt
from passlib.context import CryptContext

# Work with DB.
from database.connect import PGConnection

# Models and schemas for readability and correct operation of the code.
from models.user_data import UserRegister, UserInDB, UserInToken
from models.verify import Token
from schemas.settings import JWT
from schemas.user_data import UserInToken as SchemaUserInToken, UserInDB as SchemaUserInDB


class HashPassword:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    async def verify_password(cls, plain_password, hashed_password) -> Awaitable[bool]:
        return cls.pwd_context.verify(plain_password, hashed_password)

    @classmethod
    async def get_password_hash(cls, password: str) -> Awaitable[str]:
        return cls.pwd_context.hash(password)


class JWTToken:
    @staticmethod
    async def create_token(
        data: UserInToken,
        token_info: JWT
    ) -> Awaitable[str]:
        to_encode: SchemaUserInToken = data.model_dump()
        expire: timedelta = datetime.now() + timedelta(minutes=token_info.expire)
        to_encode.update({"expires_delta": str(expire)})
        encoded_jwt: str = encode(to_encode, token_info.secret_key, algorithm=token_info.algorithm)
        return Token(
            access_token=encoded_jwt,
            token_type="bearer",
            expires_delta=str(expire)
        )

    @staticmethod
    async def decode_token(token: str, token_info: JWT) -> Awaitable[UserInToken]:
        return UserInToken(**decode(token, token_info.secret_key, [token_info.algorithm]))


async def current_user(
    db_connection: PGConnection,
    token: str,
    jwt_info: JWT
) -> Awaitable[UserInDB]:
    token_exception: HTTPException = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"} 
    )
    try:
        token: UserInToken = await JWTToken.decode_token(token, jwt_info)
        if token.model_dump().get("username") is None:
            raise token_exception
    except jwt.InvalidTokenError:
        raise token_exception
    user: Optional[SchemaUserInDB] = await db_connection.fetchrow(
        "SELECT * FROM Users WHERE login = $1", token.username 
    )
    if user is None:
        raise token_exception
    return UserInDB(**user)


async def authorization(
    db_connection: PGConnection,
    jwt_info: JWT,
    user_auth: UserRegister,
    is_register: bool = False
) -> Awaitable[str]:
    if is_register:
        await db_connection.execute(
            (
                "INSERT INTO Users(login, password, email, name, surname, patronymic) "
                "VALUES ($1, $2, $3, $4, $5, $6)"
            ),
            user_auth.login,
            await HashPassword.get_password_hash(user_auth.password),
            user_auth.email,
            user_auth.name,
            user_auth.surname,
            user_auth.patronymic
        )
    userdata: Optional[UserInDB] = await db_connection.fetchrow(
        "SELECT * FROM Users WHERE login = $1",
        user_auth.login
    )
    if userdata is None or not await HashPassword.verify_password(
        user_auth.password, userdata['password']
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    return await JWTToken.create_token(
        UserInToken(
            id=userdata['id'],
            username=userdata['login']
        ),
        jwt_info
    )
