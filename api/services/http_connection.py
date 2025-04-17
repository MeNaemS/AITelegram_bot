import aiohttp
from json import dumps
from schemas.openrouterai.request import AiRequest


class AioHttp:
    def __init__(self, openai_api_key: str):
        self.__session = aiohttp.ClientSession(
            base_url='https://openrouter.ai/api/v1/',
            headers={
                'Authorization': f'Bearer {openai_api_key}',
                'Content-Type': 'application/json',
            }
        )

    @property
    def session(self) -> aiohttp.ClientSession:
        return self.__session

    async def post(self, url, json: AiRequest):
        async with self.__session.post(url, data=dumps(json)) as response:
            return await response.json()

    async def close(self):
        await self.__session.close()
