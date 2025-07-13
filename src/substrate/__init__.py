"""Substrate - System Architect MCP Server

This module implements the substrate MCP server that serves as the system architect,
providing documentation and methodology for the entire system.
"""

from .server import SubstrateServer
from .base import SubstrateMCP, HermesExecutor, ExecutionRequest, ExecutionResult
from .errors import SubstrateError, ValidationError, NotFoundError
from .components import ResponseBuilder, ProgressTracker, SamplingManager

__version__ = "1.0.0"

__all__ = [
    # Server
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
]
