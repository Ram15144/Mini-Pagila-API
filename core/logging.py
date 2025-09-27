"""Structured logging configuration using structlog."""

import logging
import sys
from typing import Any, Dict
import structlog
from structlog.typing import EventDict, Processor
import uuid
from contextvars import ContextVar

from core.config import settings


# Context variable for correlation ID
correlation_id_var: ContextVar[str] = ContextVar('correlation_id', default='')


def get_correlation_id() -> str:
    """Get the current correlation ID."""
    return correlation_id_var.get()


def set_correlation_id(correlation_id: str = None) -> str:
    """Set a new correlation ID and return it."""
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())
    correlation_id_var.set(correlation_id)
    return correlation_id


def add_correlation_id(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add correlation ID to log entries."""
    correlation_id = get_correlation_id()
    if correlation_id:
        event_dict["correlation_id"] = correlation_id
    return event_dict


def add_service_context(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add service context information."""
    event_dict["service"] = "pagila-api"
    event_dict["version"] = "0.1.0"
    return event_dict


def filter_health_checks(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Filter out health check logs to reduce noise."""
    # Skip health check logs unless there's an error
    if (event_dict.get("path") == "/health" and 
        event_dict.get("status_code", 200) < 400):
        raise structlog.DropEvent
    return event_dict


def configure_logging() -> None:
    """Configure structured logging for the application."""
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
    )
    
    # Configure processors based on environment
    processors: list[Processor] = [
        structlog.stdlib.filter_by_level,
        add_correlation_id,
        add_service_context,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    
    # Add environment-specific processors
    if settings.debug:
        # Development: Human-readable colored output
        processors.extend([
            structlog.dev.ConsoleRenderer(colors=True),
        ])
    else:
        # Production: JSON output for structured logging
        processors.extend([
            structlog.processors.JSONRenderer()
        ])
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        context_class=dict,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = None) -> structlog.BoundLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name (defaults to calling module)
        
    Returns:
        Configured structlog BoundLogger instance
    """
    return structlog.get_logger(name)


# Convenience loggers for different components
app_logger = get_logger("app")
api_logger = get_logger("api")  
service_logger = get_logger("service")
repository_logger = get_logger("repository")
auth_logger = get_logger("auth")
ai_logger = get_logger("ai")


class LoggingMixin:
    """Mixin class to add logging capabilities to any class."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = get_logger(self.__class__.__name__)
    
    def log_operation_start(self, operation: str, **kwargs) -> None:
        """Log the start of an operation."""
        self.logger.info(
            f"{operation} started",
            operation=operation,
            component=self.__class__.__name__,
            **kwargs
        )
    
    def log_operation_success(self, operation: str, **kwargs) -> None:
        """Log successful completion of an operation."""
        self.logger.info(
            f"{operation} completed successfully",
            operation=operation,
            component=self.__class__.__name__,
            status="success",
            **kwargs
        )
    
    def log_operation_error(self, operation: str, error: Exception, **kwargs) -> None:
        """Log an operation error."""
        self.logger.error(
            f"{operation} failed",
            operation=operation,
            component=self.__class__.__name__,
            status="error",
            error_type=type(error).__name__,
            error_message=str(error),
            **kwargs
        )
    
    def log_validation_error(self, operation: str, validation_errors: list, **kwargs) -> None:
        """Log validation errors."""
        self.logger.warning(
            f"{operation} validation failed",
            operation=operation,
            component=self.__class__.__name__,
            status="validation_error",
            validation_errors=validation_errors,
            **kwargs
        )


class RequestLogger:
    """Request/response logging utilities."""
    
    @staticmethod
    def log_request(method: str, path: str, **kwargs) -> None:
        """Log incoming HTTP request."""
        api_logger.info(
            "Request received",
            method=method,
            path=path,
            **kwargs
        )
    
    @staticmethod
    def log_response(method: str, path: str, status_code: int, duration_ms: float, **kwargs) -> None:
        """Log HTTP response."""
        log_level = "error" if status_code >= 400 else "info"
        
        getattr(api_logger, log_level)(
            "Request completed",
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=round(duration_ms, 2),
            **kwargs
        )


class DatabaseLogger:
    """Database operation logging utilities."""
    
    @staticmethod
    def log_query(operation: str, table: str = None, **kwargs) -> None:
        """Log database query."""
        repository_logger.debug(
            f"Database {operation}",
            operation=operation,
            table=table,
            **kwargs
        )
    
    @staticmethod
    def log_query_result(operation: str, result_count: int = None, **kwargs) -> None:
        """Log database query results."""
        repository_logger.debug(
            f"Database {operation} completed",
            operation=operation,
            result_count=result_count,
            **kwargs
        )


class AILogger:
    """AI operation logging utilities."""
    
    @staticmethod
    def log_ai_request(operation: str, model: str, **kwargs) -> None:
        """Log AI service request."""
        ai_logger.info(
            f"AI {operation} started",
            operation=operation,
            model=model,
            **kwargs
        )
    
    @staticmethod
    def log_ai_response(operation: str, model: str, token_count: int = None, **kwargs) -> None:
        """Log AI service response."""
        ai_logger.info(
            f"AI {operation} completed",
            operation=operation,
            model=model,
            token_count=token_count,
            **kwargs
        )
    
    @staticmethod
    def log_ai_error(operation: str, error: Exception, **kwargs) -> None:
        """Log AI service error."""
        ai_logger.error(
            f"AI {operation} failed",
            operation=operation,
            error_type=type(error).__name__,
            error_message=str(error),
            **kwargs
        )
