import logging

from fastapi import FastAPI, Response, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from oidc_client import utils
from oidc_client import config


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
            url=utils.get_authorize_url()
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
            url=utils.get_authorize_url()
        )

    return Response(status_code=status.HTTP_200_OK)


@app.api_route(
    "/oidc/callback",
    methods=["GET", "POST", "HEAD"]
)
async def oidc_callback(
    request: Request,
) -> Response:
    """
    OIDC callback

    After successful authentication OIDC provider will send a POST
    to this endpoint.
    The important parts from the incoming request are:
        - `code`
        - `state`

    Both `code` and `state` are used to retrieve access token and user token
    from the OIDC provider.
    """
    # get "code" from query params `request.query_params`
    # use code to obtain access tokens by posting to auth endpoint
    """
    auth_server_url(
        window.__PAPERMERGE_RUNTIME_CONFIG__.oidc.client_id,
        payload?.code,
        window.__PAPERMERGE_RUNTIME_CONFIG__.oidc.redirect_url,
        payload?.state,
    );
    fetch(url, { method:'POST' })
      .then(response => response.json())
      .then(
        data => {
          console.log(data);
          console.log(`Redirecting to the origin ${window.location.origin}/app`);
          window.location.href = `${window.location.origin}/app`;
        }
      ).catch(error => {
        console.log(`There was an error ==='${error}'===`);
      });
    """

    return Response(status_code=status.HTTP_200_OK)
