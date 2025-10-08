#!/usr/bin/env sh
set -eu

APP_UID="${APP_UID:-10001}"
APP_GID="${APP_GID:-10001}"
APP_USER="${APP_USER:-appuser}"

mkdir -p /app/data /app/logs

# Only chown if needed (fast on big volumes)
need_chown() {
  stat -c '%u' "$1" 2>/dev/null || stat -f '%u' "$1" 2>/dev/null
}

for d in /app/data /app/logs; do
  [ -d "$d" ] || mkdir -p "$d"
  if [ "$(need_chown "$d")" != "$APP_UID" ]; then
    chown -R "$APP_UID:$APP_GID" "$d"
  fi
done

# Group-writable by default (handy if you ever use fsGroup)
umask 0002

# Drop privileges and exec the app
exec gosu "$APP_UID:$APP_GID" "$@"
