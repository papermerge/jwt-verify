#!/bin/bash

exec_server() {
  VIRTUAL_ENV=/app/venv && cd /app/
  exec poetry run uvicorn oidc_app.main:app --port 8010
}

case $1 in
  server)
    exec_server
    ;;
  *)
    exec "$@"
    ;;
esac