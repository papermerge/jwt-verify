"""
Notes:
Access tokens typically have a shorter life span while refresh tokens have a
longer one

References:
 - https://curity.io/resources/learn/oauth-refresh/
"""

import redis.asyncio as redis
import json
from . import types, config


settings = config.get_settings()
store = redis.from_url(settings.redis_url)


async def save_token(key: str, token: types.TokenData) -> None:
    """key is access token in base64 format"""
    value = token.model_dump_json()

    await store.set(
        name=f"access_{key}",
        value=value,
        ex=token.expires_in
    )
    await store.set(
        name=f"refresh_{key}",
        value=value,
        ex=token.refresh_expires_in  # this longer TTL as `expires_in`
    )


async def get_token(key: str) -> tuple[types.TokenData | None, bool]:
    """`key` is access token in base64 format"""
    access_expired = False
    # first retrieve token data using `access_{key}`
    value: str = await store.get(f"access_{key}")

    if value is None:
        # if we are here, it means that access token has expired!
        access_expired = True
        # OK, now we know that access token has expired, but still we don't have
        # token data. Let's get token data using `refresh_{key}`
        # This approach works as refresh token has longer TTL as access token
        value = await store.get(f"refresh_{key}")
        if value is None:
            # this means, both access_token and refresh_token had expired
            return None, True

    dict_value = json.loads(value)
    return types.TokenData(**dict_value), access_expired
