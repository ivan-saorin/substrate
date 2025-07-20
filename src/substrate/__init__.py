"""Substrate - Foundation for all Atlas MCP servers

This module provides base classes and components for building MCP servers
in the Atlas cognitive manipulation system.
"""

from .base import SubstrateMCP, HermesExecutor, ExecutionRequest, ExecutionResult
from .errors import SubstrateError, ValidationError, NotFoundError
from .components import ResponseBuilder, ProgressTracker, SamplingManager, ReferenceManager
from .server import SubstrateServer

__version__ = "1.0.0"

__all__ = [
    # Server (documentation server)
    "SubstrateServer",
    
    # Base classes
    "SubstrateMCP",
    "HermesExecutor",
    "ExecutionRequest", 
    "ExecutionResult",
    
    # Errors
    "SubstrateError",
    "ValidationError",
    "NotFoundError",
    
    # Components
    "ResponseBuilder",
    "ProgressTracker",
    "SamplingManager",
    "ReferenceManager",
]
