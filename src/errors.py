"""Error handling utilities for Substrate MCP servers."""

import logging
import traceback
from typing import Any, Dict, List, Optional, Type

from .types import ErrorInfo

logger = logging.getLogger(__name__)


class SubstrateError(Exception):
    """Base exception for Substrate MCP errors."""
    
    def __init__(
        self,
        message: str,
        *,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None
    ):
        """Initialize Substrate error.
        
        Args:
            message: Error message
            code: Optional error code
            details: Optional error details
            suggestions: Optional suggestions for fixing
        """
        super().__init__(message)
        self.code = code
        self.details = details or {}
        self.suggestions = suggestions or []
        
    def to_error_info(self) -> ErrorInfo:
        """Convert to ErrorInfo model."""
        return ErrorInfo(
            message=str(self),
            code=self.code,
            type=self.__class__.__name__,
            details=self.details,
            suggestions=self.suggestions,
            traceback=traceback.format_exc() if logger.isEnabledFor(logging.DEBUG) else None
        )


class ValidationError(SubstrateError):
    """Validation error."""
    
    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        """Initialize validation error."""
        if field:
            kwargs.setdefault("details", {})["field"] = field
        super().__init__(message, code="VALIDATION_ERROR", **kwargs)


class NotFoundError(SubstrateError):
    """Resource not found error."""
    
    def __init__(self, resource_type: str, resource_id: str, **kwargs):
        """Initialize not found error."""
        message = f"{resource_type} '{resource_id}' not found"
        kwargs.setdefault("details", {}).update({
            "resource_type": resource_type,
            "resource_id": resource_id
        })
        super().__init__(message, code="NOT_FOUND", **kwargs)


class PermissionError(SubstrateError):
    """Permission denied error."""
    
    def __init__(self, action: str, resource: Optional[str] = None, **kwargs):
        """Initialize permission error."""
        message = f"Permission denied for action: {action}"
        if resource:
            message += f" on resource: {resource}"
            kwargs.setdefault("details", {})["resource"] = resource
        kwargs.setdefault("details", {})["action"] = action
        super().__init__(message, code="PERMISSION_DENIED", **kwargs)


class RateLimitError(SubstrateError):
    """Rate limit exceeded error."""
    
    def __init__(
        self,
        limit: int,
        window: str,
        retry_after: Optional[int] = None,
        **kwargs
    ):
        """Initialize rate limit error."""
        message = f"Rate limit exceeded: {limit} requests per {window}"
        details = {
            "limit": limit,
            "window": window
        }
        if retry_after:
            details["retry_after_seconds"] = retry_after
            kwargs.setdefault("suggestions", []).append(
                f"Please wait {retry_after} seconds before retrying"
            )
        kwargs.setdefault("details", {}).update(details)
        super().__init__(message, code="RATE_LIMIT_EXCEEDED", **kwargs)


class TimeoutError(SubstrateError):
    """Operation timeout error."""
    
    def __init__(self, operation: str, timeout_seconds: float, **kwargs):
        """Initialize timeout error."""
        message = f"Operation '{operation}' timed out after {timeout_seconds}s"
        kwargs.setdefault("details", {}).update({
            "operation": operation,
            "timeout_seconds": timeout_seconds
        })
        kwargs.setdefault("suggestions", []).extend([
            "Try breaking the operation into smaller chunks",
            "Increase the timeout if possible",
            "Check if the service is responding slowly"
        ])
        super().__init__(message, code="TIMEOUT", **kwargs)


class ExternalServiceError(SubstrateError):
    """External service error."""
    
    def __init__(
        self,
        service: str,
        original_error: Optional[str] = None,
        **kwargs
    ):
        """Initialize external service error."""
        message = f"External service '{service}' error"
        if original_error:
            message += f": {original_error}"
            kwargs.setdefault("details", {})["original_error"] = original_error
        kwargs.setdefault("details", {})["service"] = service
        super().__init__(message, code="EXTERNAL_SERVICE_ERROR", **kwargs)


def format_error_response(
    error: Exception,
    *,
    include_traceback: bool = False,
    suggestions: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Format an exception as a standard error response.
    
    Args:
        error: The exception to format
        include_traceback: Whether to include traceback
        suggestions: Optional suggestions to add
        
    Returns:
        Formatted error response dict
    """
    from .responses import ResponseBuilder
    builder = ResponseBuilder()
    
    if isinstance(error, SubstrateError):
        # Use our error info
        error_info = error.to_error_info()
        if suggestions:
            error_info.suggestions.extend(suggestions)
            
        return builder.error(
            error_info.message,
            error_code=error_info.code,
            details=error_info.details,
            suggestions=error_info.suggestions
        )
    else:
        # Generic error
        error_msg = str(error)
        details = {
            "error_type": type(error).__name__
        }
        
        if include_traceback or logger.isEnabledFor(logging.DEBUG):
            details["traceback"] = traceback.format_exc()
            
        return builder.error(
            error_msg,
            error_code="INTERNAL_ERROR",
            details=details,
            suggestions=suggestions or [
                "This is an unexpected error. Please try again.",
                "If the problem persists, please report it."
            ]
        )


def handle_errors(
    *error_handlers: tuple[Type[Exception], Callable[[Exception], Dict[str, Any]]]
):
    """Decorator to handle specific errors with custom handlers.
    
    Usage:
        @handle_errors(
            (ValueError, lambda e: {"error": "Invalid value"}),
            (KeyError, lambda e: {"error": f"Missing key: {e}"})
        )
        async def my_function():
            ...
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # Check custom handlers
                for error_type, handler in error_handlers:
                    if isinstance(e, error_type):
                        return handler(e)
                        
                # Default handling
                logger.error(f"Unhandled error in {func.__name__}: {e}")
                return format_error_response(e)
                
        return wrapper
    return decorator
