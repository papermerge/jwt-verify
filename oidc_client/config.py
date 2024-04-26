from functools import lru_cache
from enum import Enum
from pydantic_settings import BaseSettings


class Algs(str, Enum):
    HS256 = "HS256"
    HS384 = "HS384"
    HS512 = "HS512"
    RS256 = "RS256"
    RS384 = "RS384"
    RS512 = "RS512"
    ES256 = "ES256"
    ES384 = "ES384"
    ES512 = "ES512"


class Settings(BaseSettings):
    client_secret: str
    client_id: str
    authorize_endpoint: str
    algorithms: list[Algs] = ['ES512']


@lru_cache()
def get_settings():
    return Settings()
