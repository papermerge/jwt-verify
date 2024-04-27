import logging

from fastapi import FastAPI, Response, Request, status
from fastapi.responses import RedirectResponse, PlainTextResponse
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import httpx

from oidc_client import utils, config, types, cache, http_client


app = FastAPI()


settings = config.get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logger = logging.getLogger(__name__)


@app.get("/verify")
async def verify_endpoint(
    request: Request,
) -> Response:
    access_token = utils.get_token(request)
    result = Response(status_code=status.HTTP_200_OK)

    if not access_token:
        return RedirectResponse(status_code=307, url=utils.authorize_url())

    try:
        jwt.decode(
            access_token,
            settings.client_secret,
            algorithms=settings.algorithms
        )
    except JWTError:
        return RedirectResponse(status_code=307, url=utils.authorize_url())

    token_data, access_expired = await cache.get_token(access_token)
    if token_data is None:
        logger.warning(
            f"expired token: access_token={access_token} "
            f"token_data={token_data}"
        )
        return RedirectResponse(status_code=307, url=utils.authorize_url())

    if token_data.access_token != access_token:
        logger.error(
            "cached token differs from original"
            f"access_token={access_token} "
            f"token_data={token_data}"
        )
        msg = "cached token differs from original"
        return PlainTextResponse(status_code=500, content=msg)

    if access_expired:
        new_token_data = await http_client.refresh_token(token_data)
        if new_token_data is None:
            logger.debug(f"Was not able to renew {token_data}")
            return RedirectResponse(status_code=307, url=utils.authorize_url())

        await cache.save_token(
            key=new_token_data.access_token,
            token=new_token_data
        )
        result.set_cookie('access_token', value=new_token_data.access_token)

    return result


@app.api_route(
    "/oidc/callback",
    methods=["GET", "POST", "HEAD"]
)
async def oidc_callback(
    request: Request,
) -> Response:
    async with httpx.AsyncClient() as client:
        params = {
            'client_id': settings.client_id,
            'client_secret': settings.client_secret,
            'code': request.query_params['code'],
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
            return Response(
                status_code=response.status_code,
                content=response.content,
            )

        data = response.json()
        logger.debug(f"response.json={data}")
        token = types.TokenData(
            access_token=data['access_token'],
            expires_in=data['expires_in'],
            refresh_token=data['refresh_token'],
            refresh_expires_in=data['refresh_expires_in'],
            scope=data['scope'],
            token_type=data['token_type']
        )
        await cache.save_token(key=token.access_token, token=token)
        result = Response(status_code=status.HTTP_200_OK)

        result.set_cookie('access_token', value=token.access_token)

    return result
