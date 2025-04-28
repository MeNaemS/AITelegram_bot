"""
A service that performs token validation, encoding and decoding,
	and recording a new user in the database.
"""
# Importing the typing module, datetime module
from typing import Optional, Awaitable
from datetime import datetime, timedelta

# To display the status code related to authorization/authentication.
from fastapi import HTTPException, status

# To create a token and also hash the password.
from jwt import encode, decode, InvalidTokenError
from passlib.context import CryptContext

# Work with DB.
from database.connect import PGConnection

# Models and schemas for readability and correct operation of the code.
from schemas.user_data import UserInToken as SchemaUserInToken, UserInDB as SchemaUserInDB
from models.user_data import UserRegister, UserInDB, UserInToken
from schemas.settings import JWT
from models.verify import Token


#						-- Hash password --
class HashPassword:
	pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

	@classmethod
	async def verify_password(cls, plain_password: str, hashed_password: str) -> Awaitable[bool]:
		"""Verify the password."""
		return cls.pwd_context.verify(plain_password, hashed_password)

	@classmethod
	async def get_password_hash(cls, password: str) -> Awaitable[str]:
		"""Get the password hash."""
		return cls.pwd_context.hash(password)


#						-- JWT token --
class JWTToken:
	@staticmethod
	async def create_token(
		data: UserInToken,
		token_info: JWT
	) -> Awaitable[Token]:
		"""Create a token."""
		to_encode: SchemaUserInToken = data.model_dump()
		encoded_jwt: str = encode(
			to_encode,
			token_info.secret_key,
			algorithm=token_info.algorithm
		)
		return Token(
			access_token=encoded_jwt,
			token_type="bearer",
			expires_delta=data.expires_delta
		)

	@staticmethod
	async def decode_token(token: str, token_info: JWT) -> Awaitable[UserInToken]:
		"""Decode a token."""
		return UserInToken(**decode(token, token_info.secret_key, [token_info.algorithm]))


#					-- Current user --
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
		decoded_token: UserInToken = await JWTToken.decode_token(token, jwt_info)
		if decoded_token.model_dump().get("username") is None:
			raise token_exception
		if "expires_delta" in decoded_token.model_dump():
			expiration_time = datetime.fromisoformat(decoded_token.expires_delta)
			if datetime.now() > expiration_time:
				raise token_exception
	except InvalidTokenError:
		raise token_exception
	user: Optional[SchemaUserInDB] = await db_connection.fetchrow(
		"SELECT * FROM Users WHERE login = $1", decoded_token.username 
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
			detail="Invalid login or password"
		)
	return await JWTToken.create_token(
		UserInToken(
			id=userdata['id'],
			expires_delta=str(datetime.now() + timedelta(minutes=jwt_info.expire)),
			username=userdata['login']
		),
		jwt_info
	)
