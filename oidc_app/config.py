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
    papermerge__auth__oidc_client_secret: str
    papermerge__auth__oidc_client_id: str
    papermerge__auth__oidc_access_token_url: str
    # OIDC provider "authorize" endpoint
    # for Keycloak it is <domain>/realms/<realm>/protocol/openid-connect/auth
    papermerge__auth__oidc_authorize_url: str
    # OIDC provider "token" endpoint
    # for Keycloak it is <domain>/realms/<realm>/protocol/openid-connect/token
    papermerge__auth__access_token_url: str
    algorithms: list[Algs] = ['RS256']
    # `public_key` actually can be extracted from OIDC provider
    # TODO: extract public keu from OIDC provider
    public_key: Path  # path to public key file; used to validate jwt tokens
    redis_url: str  # as cache store
    cookie_name: str = 'access_token'
    home_url: str # TODO: to be extracted from well known OIDC config


@lru_cache()
def get_settings():
    return Settings()
