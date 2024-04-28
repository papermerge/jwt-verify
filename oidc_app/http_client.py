import logging
import httpx
from . import types, config

settings = config.get_settings()
logger = logging.getLogger(__name__)


async def get_token(code: str) -> tuple[
    types.TokenData | None,
    int,
    bytes
]:
    async with httpx.AsyncClient() as client:
        params = {
            'client_id': settings.client_id,
            'client_secret': settings.client_secret,
            'code': code,
            'grant_type': 'authorization_code'
        }
        logger.debug(f"params: {params}")

        response = await client.post(
            settings.access_token_endpoint,
            data=params,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )
        logger.debug(
            f"response_code = {response.status_code}"
        )
        logger.debug(f"response_text = {response.text}")

        if not response.is_success:
            message = " ".join([
                f"response.status_code = {response.status_code}",
                f"response.text = {response.text}"
                f"response.content = {response.content}"
            ])
            logger.debug(message)
            return None, response.status_code, response.content

        data = response.json()
        logger.debug(f"response.json={data}")
        token_data = types.TokenData(
            access_token=data['access_token'],
            expires_in=data['expires_in'],
            refresh_token=data['refresh_token'],
            refresh_expires_in=data['refresh_expires_in'],
            scope=data['scope'],
            token_type=data['token_type']
        )

        return token_data, response.status_code, response.content


async def refresh_token(old_token: types.TokenData) -> tuple[
    types.TokenData | None,
    int,
    bytes
]:
    async with httpx.AsyncClient() as client:
        params = {
            'client_id': settings.client_id,
            'client_secret': settings.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': old_token.refresh_token
        }
        logger.debug(f"params: {params}")

        response = await client.post(
            settings.access_token_endpoint,
            data=params,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )
        logger.debug(
            f"response_code = {response.status_code}"
        )
        logger.debug(f"response_text = {response.text}")

        if not response.is_success:
            message = " ".join([
                f"response.status_code = {response.status_code}",
                f"response.text = {response.text}"
                f"response.content = {response.content}"
            ])
            logger.debug(message)
            return None, response.status_code, response.content

        data = response.json()
        logger.debug(f"response.json={data}")

        token_data = types.TokenData(
            access_token=data['access_token'],
            expires_in=data['expires_in'],
            refresh_token=data['refresh_token'],
            refresh_expires_in=data['refresh_expires_in'],
            scope=data['scope'],
            token_type=data['token_type']
        )

    return token_data, response.status_code, response.content
