#!/bin/zsh
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE_FILE="$REPO_DIR/docker-compose.yml"
SERVICE_NAME="vinted-notifications"
LOG_FILE="$REPO_DIR/scripts/docker_watchdog.log"
CHECK_INTERVAL=30
DOCKER_SOCKET="${DOCKER_SOCKET:-$HOME/.docker/run/docker.sock}"

COMPOSE_HTTP_TIMEOUT="${COMPOSE_HTTP_TIMEOUT:-10}"
export COMPOSE_HTTP_TIMEOUT

log() {
  local ts
  ts="$(date '+%Y-%m-%d %H:%M:%S')"
  echo "${ts} - $1" | tee -a "$LOG_FILE"
}

docker_ping() {
  python3 - "$DOCKER_SOCKET" <<'PY'
import socket, sys
sock_path = sys.argv[1]
try:
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(2.0)
    s.connect(sock_path)
    s.sendall(b"GET /_ping HTTP/1.0\r\n\r\n")
    data = s.recv(1024)
    status_line = data.split(b"\r\n", 1)[0]
    if b" 200 " in status_line:
        sys.exit(0)
    sys.exit(1)
except Exception:
    sys.exit(1)
PY
}

wait_for_docker() {
  local attempts=0
  until docker_ping; do
    attempts=$((attempts + 1))
    if (( attempts == 1 )); then
      log "Waiting for Docker Desktop to become available..."
    fi
    sleep 2
  done
  log "Docker Desktop is ready."
}

restart_docker_desktop() {
  log "Docker daemon unreachable/unhealthy. Restarting Docker Desktop..."
  osascript -e 'quit app "Docker"' >/dev/null 2>&1 || true
  sleep 2
  open -g -a Docker >/dev/null 2>&1 || {
    log "Failed to launch Docker.app automatically."
    return 1
  }
  wait_for_docker
}

ensure_stack() {
  log "Ensuring compose stack is running..."
  docker compose -f "$COMPOSE_FILE" up -d >/dev/null 2>&1 && log "Compose stack is up."
}

check_compose_service() {
  docker compose -f "$COMPOSE_FILE" ps --status running --services 2>/dev/null | grep -qx "$SERVICE_NAME"
}

while true; do
  if ! docker_ping; then
    restart_docker_desktop || true
    sleep 2
    continue
  fi

  if ! check_compose_service; then
    log "Service $SERVICE_NAME is not running; attempting to start it."
    ensure_stack
  fi

  sleep "$CHECK_INTERVAL"

done
