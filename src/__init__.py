"""
Substrate - Foundation layer for AI applications
Provides MCP protocol, multi-provider support, evaluation, and filesystem utilities
"""

__version__ = "1.0.0"

# Re-export main components for easy access
from .mcp.server import FastMCP
from .providers import (
    Provider,
    ProviderType,
    LocalProvider,
    OpenAIProvider,
    AnthropicAPIProvider,
    GoogleProvider,
    ProviderManager
)
from .evaluation import EvaluationEngine
from .filesystem import FileSystemManager

__all__ = [
    # MCP
    "FastMCP",
    
    # Providers
    "Provider",
    "ProviderType",
    "LocalProvider",
    "OpenAIProvider",
    "AnthropicAPIProvider",
    "GoogleProvider",
    "ProviderManager",
    
    # Evaluation
    "EvaluationEngine",
    
    # Filesystem
    "FileSystemManager"
]
