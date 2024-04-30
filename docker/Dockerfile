FROM python:3.11-slim-bookworm

ENV APP_DIR=/oidc_app
WORKDIR ${APP_DIR}

COPY poetry.lock pyproject.toml README.md ${APP_DIR}/
COPY oidc_app/ ${APP_DIR}/oidc_app/

RUN pip install --upgrade poetry && python -m venv "${APP_DIR}/venv"
ENV VIRTUAL_ENV "${APP_DIR}/venv"
RUN poetry install --without dev

COPY docker/run.bash /run.bash
RUN chmod +x /run.bash

ENTRYPOINT ["/run.bash"]
