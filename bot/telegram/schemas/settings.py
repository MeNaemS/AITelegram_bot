from dataclasses import dataclass


@dataclass
class Bot:
    name: str
    token: str
    login: str
    password: str


@dataclass
class API:
    host: str
    port: int


@dataclass
class Settings:
    bot: Bot
    api: API
