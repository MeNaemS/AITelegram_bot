import aiohttp
from schemas.ai_request import AiRequest


class AioHttp:
    def __init__(self, openai_api_key: str):
        self.__session = aiohttp.ClientSession(
            base_url='https://openrouter.ai/api/v1/chat/completions/',
            headers={
                'Authorization': f'Bearer {openai_api_key}',
                'Content-Type': 'application/json',
            }
        )

    @property
    def session(self) -> aiohttp.ClientSession:
        return self.__session

    async def post(self, json: AiRequest):
        async with self.__session.post(json=json) as response:
            return await response.json()

    async def close(self):
        await self.__session.close()
