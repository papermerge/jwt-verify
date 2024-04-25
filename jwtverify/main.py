import logging

from fastapi import FastAPI, Response, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from jwtverify import utils
from jwtverify import config


app = FastAPI()


settings = config.get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logger = logging.getLogger(__name__)


@app.get("/verify")
async def verify_endpoint(
    request: Request,
) -> Response:
    token = utils.get_token(request)

    if not token:
        return RedirectResponse(
            status_code=307,
            url=settings.redirect_url
        )

    try:
        jwt.decode(
            token,
            settings.client_secret,
            algorithms=settings.algorithms
        )
    except JWTError:
        return RedirectResponse(
            status_code=307,
            url=settings.redirect_url
        )

    return Response(status_code=status.HTTP_200_OK)
