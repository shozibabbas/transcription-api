"""Application entry point with logging, middleware, and exception handler setup."""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Callable

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app import create_app
from app.config import settings


# Configure logging
def setup_logging(log_level: str = settings.LOG_LEVEL) -> logging.Logger:
    """Configure application logging with file and console handlers.

    Args:
        log_level: Log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    console_formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
    )
    file_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    file_formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger


# Logging middleware
class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log HTTP request and response details."""

    def __init__(self, app: FastAPI, logger: logging.Logger):
        """Initialize logging middleware.

        Args:
            app: FastAPI application instance
            logger: Logger instance
        """
        super().__init__(app)
        self.logger = logger

    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        """Process request and log details.

        Args:
            request: HTTP request
            call_next: Next middleware or route handler

        Returns:
            HTTP response
        """
        self.logger.info(
            f"{request.method} {request.url.path} - Client: {request.client.host if request.client else 'unknown'}"
        )

        try:
            response = await call_next(request)
            self.logger.info(
                f"Response - {request.method} {request.url.path} - Status: {response.status_code}"
            )
            return response
        except Exception as exc:
            self.logger.error(
                f"Error processing request - {request.method} {request.url.path}: {str(exc)}",
                exc_info=True,
            )
            raise


# Exception handlers
def add_exception_handlers(app: FastAPI, logger: logging.Logger) -> None:
    """Add global exception handlers to FastAPI app.

    Args:
        app: FastAPI application instance
        logger: Logger instance
    """

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """Handle ValueError exceptions.

        Args:
            request: HTTP request
            exc: Exception instance

        Returns:
            JSON error response
        """
        logger.warning(f"ValueError: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc), "error_type": "ValueError"},
        )

    @app.exception_handler(RuntimeError)
    async def runtime_error_handler(request: Request, exc: RuntimeError):
        """Handle RuntimeError exceptions.

        Args:
            request: HTTP request
            exc: Exception instance

        Returns:
            JSON error response
        """
        logger.error(f"RuntimeError: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error", "error_type": "RuntimeError"},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general unexpected exceptions.

        Args:
            request: HTTP request
            exc: Exception instance

        Returns:
            JSON error response
        """
        logger.error(
            f"Unexpected exception on {request.method} {request.url.path}: {str(exc)}",
            exc_info=True,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error", "error_type": "UnexpectedException"},
        )


def create_application() -> FastAPI:
    """Create and configure the FastAPI application with all middleware and handlers.

    Returns:
        Configured FastAPI application instance
    """
    # Setup logging
    logger = setup_logging(settings.LOG_LEVEL)
    logger.info(f"Initializing application - {settings.API_TITLE} v{settings.API_VERSION}")

    # Create base FastAPI app
    app = create_app()

    # Add logging middleware
    app.add_middleware(LoggingMiddleware, logger=logger)

    # Add exception handlers
    add_exception_handlers(app, logger)

    logger.info("Application configured successfully")
    return app


# Create application instance
app = create_application()


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.info("Starting Uvicorn server")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=None,  # Use our custom logging configuration
    )
