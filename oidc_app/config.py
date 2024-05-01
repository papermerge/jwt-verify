from functools import lru_cache
from enum import Enum
from pathlib import Path
from pydantic_settings import BaseSettings


class Algs(str, Enum):
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
    algorithms: list[Algs] = ['RS256']
    # `public_key` actually can be extracted from OIDC provider
    # TODO: extract public keu from OIDC provider
    public_key: Path  # path to public key file; used to validate jwt tokens
    redis_url: str  # as cache store
    cookie_name: str = 'access_token'
    # `home_url` actually can be extracted from OIDC provider
    home_url: str  # TODO: extract it from OIDC provider


@lru_cache()
def get_settings():
    return Settings()
