#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${APP_DIR:-}" ]]; then
  echo "APP_DIR environment variable is required" >&2
  exit 1
fi

VENV_PATH=${VENV_PATH:-"$APP_DIR/venv"}
GIT_REF=${GIT_REF:-"develop"}
PYTHON_BIN="${PYTHON_BIN:-$VENV_PATH/bin/python}"
PIP_BIN="${PIP_BIN:-$VENV_PATH/bin/pip}"
SERVICE_NAME=${SERVICE_NAME:-"hw_sp_30_1"}
ENV_FILE=${ENV_FILE:-"$APP_DIR/.env"}

if [[ ! -d "$APP_DIR" ]]; then
  echo "Application directory $APP_DIR does not exist" >&2
  exit 1
fi

cd "$APP_DIR"

echo "[deploy] Fetching latest code for $GIT_REF"
if [[ ! -d .git ]]; then
  echo "Directory $APP_DIR is not a git repository" >&2
  exit 1
fi

git fetch origin "$GIT_REF"
git checkout "$GIT_REF"
git reset --hard "origin/$GIT_REF"

echo "[deploy] Ensuring virtual environment exists at $VENV_PATH"
if [[ ! -d "$VENV_PATH" ]]; then
  python3 -m venv "$VENV_PATH"
fi

source "$VENV_PATH/bin/activate"

"$PIP_BIN" install --upgrade pip
"$PIP_BIN" install -r requirements.txt

if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

"$PYTHON_BIN" manage.py migrate --noinput
"$PYTHON_BIN" manage.py collectstatic --noinput

if command -v sudo >/dev/null 2>&1; then
  echo "[deploy] Restarting service $SERVICE_NAME via sudo"
  sudo systemctl restart "$SERVICE_NAME"
else
  echo "[deploy] Restarting service $SERVICE_NAME without sudo"
  systemctl restart "$SERVICE_NAME"
fi

echo "[deploy] Deployment completed"
