import logging

from fastapi import FastAPI, Response, Request, status
from fastapi.responses import RedirectResponse, PlainTextResponse
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from oidc_client import utils, config, cache, http_client


app = FastAPI()


settings = config.get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logger = logging.getLogger(__name__)


@app.get("/verify")
async def verify_endpoint(
    request: Request,
) -> Response:
    access_token: str = utils.get_token(request)
    result = Response(status_code=status.HTTP_200_OK)

    if not access_token:
        return RedirectResponse(status_code=307, url=utils.authorize_url())

    try:
        # is JWT signature valid?
        jwt.decode(
            access_token,
            settings.client_secret,
            algorithms=settings.algorithms
        )
    except JWTError:
        # invalid signature
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
        new_token_data, status_code, content = await http_client.refresh_token(
            token_data
        )
        if new_token_data is None:
            logger.debug(
                f"Was not able to renew {token_data} "
                f"Upstream status_code={status_code} "
                f"Upstream content={content} "
            )
            return RedirectResponse(status_code=307, url=utils.authorize_url())

        await cache.save_token(
            key=new_token_data.access_token,
            token=new_token_data
        )
        result.set_cookie('access_token', value=new_token_data.access_token)

    return result


@app.api_route("/oidc/callback", methods=["GET", "POST", "HEAD"])
async def oidc_callback(
    request: Request,
) -> Response:
    code = request.query_params['code']
    token_data, status_code, content = await http_client.get_token(code)

    if token_data is None:
        return Response(status_code=status_code, content=content)

    await cache.save_token(key=token_data.access_token, token=token_data)

    response = Response(status_code=status.HTTP_200_OK)
    response.set_cookie('access_token', value=token_data.access_token)

    return response
