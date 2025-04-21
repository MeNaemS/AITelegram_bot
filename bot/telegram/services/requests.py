import aiohttp
from typing import Optional, Dict, Any
from schemas.api_responses import AuthResponse, AIResponse


class SendRequests:
    def __init__(self, host: str, port: int, bot_login: str, bot_password: str):
        self.http_client: Optional[aiohttp.ClientSession] = None
        self.url: str = f'http://{host}:{port}'
        self.token: str = ''
        self.bot_login: str = bot_login
        self.bot_password: str = bot_password

    async def _ensure_client(self) -> aiohttp.ClientSession:
        if self.http_client is None or self.http_client.closed:
            self.http_client = aiohttp.ClientSession(
                base_url=self.url,
                headers={"Content-Type": "application/json"}
            )
        return self.http_client

    async def auth(self) -> AuthResponse:
        try:
            client = await self._ensure_client()
            async with client.post(
                '/auth/login',
                json={
                    'login': self.bot_login,
                    'password': self.bot_password
                }
            ) as response:
                if response.status == 401:
                    raise RuntimeError('Invalid login or password')
                data = await response.json()
                self.token = data['access_token']
        except RuntimeError:
            client = await self._ensure_client()
            async with client.post(
                '/auth/register',
                json={
                    'login': self.bot_login,
                    'password': self.bot_password
                }
            ) as response:
                data = await response.json()
                self.token = data['access_token']
        return data

    async def post(self, url: str, data: Dict[str, Any]) -> AIResponse:
        try:
            if not self.token:
                await self.auth()
            client = await self._ensure_client()
            async with client.post(
                url,
                headers={'token': f'{self.token}'},
                json=data
            ) as response:
                if response.status == 401:
                    raise RuntimeError('Invalid token')
                return await response.json()
        except RuntimeError:
            await self.auth()
            return await self.post(url, data)

    async def close(self):
        if self.http_client and not self.http_client.closed:
            await self.http_client.close()
