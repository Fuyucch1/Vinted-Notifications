import logging
import os
import sys
from logging.handlers import RotatingFileHandler

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)


# Custom filter to exclude specific log messages
class ExcludeFilter(logging.Filter):
    def filter(self, record):
        # Filter out APScheduler executor logs about running jobs
        if record.name == 'apscheduler.executors.default' and (
                'Running job' in record.getMessage() or
                'executed successfully' in record.getMessage()):
            return False

        # Filter out APScheduler scheduler logs about job management
        if record.name == 'apscheduler.scheduler' and (
                'Added job' in record.getMessage() or
                'Adding job tentatively' in record.getMessage() or
                'Removed job' in record.getMessage() or
                'Scheduler started' in record.getMessage() or
                'skipped: maximum number of running instances reached' in record.getMessage()):
            return False

        # Filter out httpx HTTP request logs
        if record.name == 'httpx' and 'HTTP Request:' in record.getMessage():
            return False

        # Filter out log refresh requests from the web UI
        if record.name == 'werkzeug' and 'GET /api/logs' in record.getMessage():
            return False

        return True


# Configure the root logger
def configure_root_logger():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)

    # File handler for all logs
    file_handler = RotatingFileHandler(
        'logs/vinted.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    # Create and add the exclude filter to both handlers
    exclude_filter = ExcludeFilter()
    console_handler.addFilter(exclude_filter)
    file_handler.addFilter(exclude_filter)

    # Add handlers to root logger
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)


# Get a logger for a specific module
def get_logger(name):
    if not logging.getLogger().handlers:
        configure_root_logger()
    return logging.getLogger(name)
