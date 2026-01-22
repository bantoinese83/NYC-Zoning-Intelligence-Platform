"""
Logging configuration for the application.

Sets up structured logging with appropriate formatters and handlers
for different environments (development vs production).
"""

import logging
import sys
from typing import Dict, Any

from ..config import settings


def setup_logging() -> None:
    """
    Configure logging for the application.

    Sets up different log levels and formatters for development vs production.
    """
    # Clear any existing handlers
    logging.getLogger().handlers.clear()

    # Set root logger level
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level))

    # Create formatter
    if settings.is_development:
        # Development: colorful, detailed format
        formatter = logging.Formatter(
            fmt="%(asctime)s %(levelname)s [%(name)s:%(lineno)d] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    else:
        # Production: JSON format for log aggregation
        formatter = JSONFormatter()

    # Console handler (always present)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler for production
    if settings.is_production:
        file_handler = logging.FileHandler("app.log")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        root_logger.addHandler(file_handler)

    # Set specific log levels for noisy libraries
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    logging.getLogger("geoalchemy2").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    # Log startup information
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured for {settings.environment} environment")
    logger.info(f"Log level: {settings.log_level}")

    if settings.is_development:
        logger.debug("Development mode: detailed logging enabled")
    else:
        logger.info("Production mode: structured logging enabled")


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for production logging.

    Creates structured JSON logs suitable for log aggregation systems
    like ELK stack, CloudWatch, or DataDog.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.
        """
        import json
        import datetime

        # Base log entry
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields from record
        if hasattr(record, "__dict__"):
            for key, value in record.__dict__.items():
                if key not in {
                    "name",
                    "msg",
                    "args",
                    "levelname",
                    "levelno",
                    "pathname",
                    "filename",
                    "module",
                    "exc_info",
                    "exc_text",
                    "stack_info",
                    "lineno",
                    "funcName",
                    "created",
                    "msecs",
                    "relativeCreated",
                    "thread",
                    "threadName",
                    "processName",
                    "process",
                    "message",
                }:
                    log_entry[key] = value

        # Add request context if available (would be set by middleware)
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id

        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id

        return json.dumps(log_entry, default=str)


def get_request_logger(request_id: str | None = None) -> logging.Logger:
    """
    Get a logger with request context.

    Args:
        request_id: Request identifier for tracing

    Returns:
        Logger with request context
    """
    logger = logging.getLogger("request")
    if request_id:
        # Create child logger with request context
        logger = logger.getChild(request_id)
    return logger


def log_api_request(
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    user_id: str | None = None,
    request_id: str | None = None,
) -> None:
    """
    Log API request with structured data.

    Args:
        method: HTTP method
        path: Request path
        status_code: HTTP status code
        duration_ms: Request duration in milliseconds
        user_id: User identifier (if authenticated)
        request_id: Request identifier
    """
    logger = logging.getLogger("api")

    # Choose log level based on status code
    if status_code >= 500:
        log_method = logger.error
    elif status_code >= 400:
        log_method = logger.warning
    else:
        log_method = logger.info

    log_method(
        f"{method} {path} -> {status_code} ({duration_ms:.1f}ms)",
        extra={
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": duration_ms,
            "user_id": user_id,
            "request_id": request_id,
        },
    )


def log_database_query(
    query: str, duration_ms: float, params: Dict[str, Any] | None = None
) -> None:
    """
    Log database query performance.

    Args:
        query: SQL query string
        duration_ms: Query execution time
        params: Query parameters
    """
    logger = logging.getLogger("database")

    # Log slow queries at warning level
    if duration_ms > 500:  # 500ms threshold
        logger.warning(
            f"Slow query: {duration_ms:.1f}ms",
            extra={
                "query": query[:500] + "..." if len(query) > 500 else query,
                "duration_ms": duration_ms,
                "params": params,
            },
        )
    else:
        logger.debug(
            f"Query executed in {duration_ms:.1f}ms",
            extra={
                "query": query[:200] + "..." if len(query) > 200 else query,
                "duration_ms": duration_ms,
            },
        )
