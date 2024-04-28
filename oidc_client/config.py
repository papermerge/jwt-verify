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
    client_secret: str  # i.e. OIDC client secret
    client_id: str      # i.e. OIDC client secret
    # OIDC provider "authorize" endpoint
    # for Keycloak it is <domain>/realms/<realm>/protocol/openid-connect/auth
    authorize_endpoint: str
    # OIDC provider "token" endpoint
    # for Keycloak it is <domain>/realms/<realm>/protocol/openid-connect/token
    access_token_endpoint: str
    algorithms: list[Algs] = ['HS256']
    redis_url: str  # as cache store
    cookie_name: str = 'access_token'


@lru_cache()
def get_settings():
    return Settings()
