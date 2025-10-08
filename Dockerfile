FROM python:3.11-slim

# --- build args / defaults for the runtime user ---
ARG APP_UID=10001
ARG APP_GID=10001
ARG APP_USER=appuser

WORKDIR /app

# System deps: gosu to drop privileges cleanly
RUN apt-get update \
 && apt-get install -y --no-install-recommends gosu \
 && rm -rf /var/lib/apt/lists/*

# Create runtime user/group and app dirs (inside image)
RUN groupadd -g ${APP_GID} ${APP_USER} \
 && useradd -u ${APP_UID} -g ${APP_GID} -M ${APP_USER} \
 && mkdir -p /app/data /app/logs

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# EntryPoint script (added below)
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Expose ports
EXPOSE 8000
EXPOSE 8080

# Run as root for the entrypoint to adjust ownership if needed,
# then the entrypoint will drop to ${APP_USER}.
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["python", "vinted_notifications.py"]