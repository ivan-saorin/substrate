"""Substrate MCP Foundation - Base framework for MCP servers."""

from .base import SubstrateMCP
from .errors import (
    SubstrateError,
    ValidationError,
    NotFoundError,
    PermissionError,
    RateLimitError,
    TimeoutError,
    ExternalServiceError,
    format_error_response,
    handle_errors,
)
from .progress import (
    ProgressTracker,
    OperationTracker,
    ProgressContext,
    estimate_progress,
)
from .responses import ResponseBuilder
from .sampling import SamplingManager, SamplingContext
from .types import (
    Tool,
    ToolParameter,
    ToolResponse,
    SamplingRequest,
    Annotation,
    ResponseMetadata,
    ProgressUpdate,
    ErrorInfo,
    PromptDefinition,
    ProviderConfig,
    ComparisonResult,
    Campaign,
)
from .utils import (
    generate_id,
    hash_content,
    truncate_string,
    format_duration,
    format_size,
    deep_merge,
    sanitize_filename,
    retry_async,
    chunk_list,
    flatten_dict,
    Timer,
)

__version__ = "2.0.0"

__all__ = [
    # Base class
    "SubstrateMCP",
    
    # Errors
    "SubstrateError",
    "ValidationError", 
    "NotFoundError",
    "PermissionError",
    "RateLimitError",
    "TimeoutError",
    "ExternalServiceError",
    "format_error_response",
    "handle_errors",
    
    # Progress tracking
    "ProgressTracker",
    "OperationTracker",
    "ProgressContext",
    "estimate_progress",
    
    # Response building
    "ResponseBuilder",
    
    # Sampling
    "SamplingManager",
    "SamplingContext",
    
    # Types
    "Tool",
    "ToolParameter",
    "ToolResponse",
    "SamplingRequest",
    "Annotation",
    "ResponseMetadata",
    "ProgressUpdate",
    "ErrorInfo",
    "PromptDefinition",
    "ProviderConfig",
    "ComparisonResult",
    "Campaign",
    
    # Utils
    "generate_id",
    "hash_content",
    "truncate_string",
    "format_duration",
    "format_size",
    "deep_merge",
    "sanitize_filename",
    "retry_async",
    "chunk_list",
    "flatten_dict",
    "Timer",
]
