from dataclasses import dataclass


@dataclass(slots=True)
class Bot:
    name: str
    token: str


@dataclass(slots=True)
class DB:
    username: str
    password: str
    host: str
    port: int
    database: str


@dataclass(slots=True)
class JWT:
    secret_key: str
    algorithm: str
    expire: int


@dataclass(slots=True)
class AI:
    models: list[str]
    ollama_host: str
    ollama_port: int


@dataclass(slots=True)
class API:
    db: DB
    jwt: JWT
    ai: AI


@dataclass(slots=True)
class Settings:
    api: API
