FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create a directory for logs
RUN mkdir -p logs

RUN useradd -u 10001 -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose the web UI port
EXPOSE 8000
# Expose the RSS feed port
EXPOSE 8080

# Command to run the application
CMD ["python", "vinted_notifications.py"]
