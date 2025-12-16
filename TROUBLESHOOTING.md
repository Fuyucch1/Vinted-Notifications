# Docker Desktop / Compose Stop Error

When trying to stop the stack from Docker Desktop, some users hit:

```
Cannot stop Docker Compose application. Reason: Max retries reached: Error invoking remote method 'containers.composeBulkAction__wrapped': Error: An object could not be cloned.
```

This appears to be a Docker Desktop UI bug rather than an issue with the container image.

## Workarounds

- Stop via CLI instead of the Docker Desktop UI:
  ```bash
  docker compose -f docker-compose.yml down
  # add -v if you intentionally want to remove the named volumes:
  # docker compose -f docker-compose.yml down -v
  ```
- If the CLI succeeds but the UI still errors, restart or update Docker Desktop.
- If the stack keeps auto-starting, make sure the watchdog script is not running (`scripts/docker_watchdog.sh` will restart Docker Desktop and bring the stack back up).

## Quick diagnostics

- Check current services: `docker compose -f docker-compose.yml ps`
- View watchdog logs (if enabled): `scripts/docker_watchdog.log`
