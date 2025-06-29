"""Substrate MCP Foundation - Base class for all MCP servers."""

import asyncio
import logging
import time
import uuid
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar

from fastmcp import FastMCP, Context
from pydantic import BaseModel, Field

from .errors import SubstrateError, format_error_response
from .progress import ProgressTracker
from .responses import ResponseBuilder
from .sampling import SamplingManager
from .types import Tool, ToolResponse

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class SubstrateMCP(ABC):
    """Base class for all MCP servers built on Substrate.
    
    Provides:
    - Automatic tool registration for self-documentation and sampling
    - Progress tracking for long operations
    - Standardized error handling
    - Response formatting utilities
    - Sampling emulation for Claude Desktop
    """
    
    def __init__(
        self,
        name: str,
        version: str,
        description: str,
        *,
        instructions: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialize a Substrate MCP server.
        
        Args:
            name: Server name (e.g., "akab", "synapse")
            version: Server version
            description: Human-readable description
            instructions: Optional instructions for the LLM
            config: Optional configuration dict
        """
        self.name = name
        self.version = version
        self.description = description
        self.config = config or {}
        
        # Initialize FastMCP
        self.mcp = FastMCP(f"{name} - {description}")
        if instructions:
            self.mcp.add_instructions(instructions)
            
        # Initialize components
        self.response_builder = ResponseBuilder()
        self.sampling_manager = SamplingManager()
        self.progress_tracker = ProgressTracker()
        
        # Setup standard tools
        self._setup_standard_tools()
        
        # Track server start time
        self._start_time = time.time()
        
        logger.info(f"Initialized {name} v{version}")

    def _setup_standard_tools(self) -> None:
        """Register standard tools that all Substrate servers must have."""
        
        # Self-documentation tool with server name
        @self.mcp.tool(name=self.name)
        async def self_documentation(ctx: Context) -> Dict[str, Any]:
            """Get information about this server and its capabilities.
            
            This tool is automatically called when users say things like:
            - "use {name} to..."
            - "what can {name} do?"
            - "help me with {name}"
            """
            # Allow subclasses to customize
            capabilities = await self.get_capabilities()
            
            response = self.response_builder.success(
                data={
                    "name": self.name,
                    "version": self.version,
                    "description": self.description,
                    "capabilities": capabilities,
                    "uptime_seconds": int(time.time() - self._start_time),
                },
                message=f"{self.name} is ready to help! Here's what I can do..."
            )
            
            # Check if we should request sampling
            if self.sampling_manager.should_request_sampling("help"):
                sampling_req = self.sampling_manager.create_request(
                    f"The user asked about {self.name}. Based on their request, "
                    f"what specific feature would be most helpful to demonstrate?"
                )
                response["_sampling_request"] = sampling_req
                
            return response
        
        # Sampling callback tool with proper naming
        @self.mcp.tool(name=f"{self.name}_sampling_callback")
        async def sampling_callback(
            ctx: Context,
            request_id: str = Field(..., description="ID from the sampling request"),
            response: str = Field(..., description="The LLM's response")
        ) -> Dict[str, Any]:
            """Handle sampling responses from the client."""
            try:
                result = await self.sampling_manager.handle_response(
                    request_id, response
                )
                return self.response_builder.success(
                    data={"processed": True, "result": result},
                    message="Sampling response processed successfully"
                )
            except Exception as e:
                logger.error(f"Sampling callback error: {e}")
                return format_error_response(e)

    @abstractmethod
    async def get_capabilities(self) -> Dict[str, Any]:
        """Return server-specific capabilities for self-documentation.
        
        Subclasses must implement this to describe their features.
        """
        pass

    def tool(
        self,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        include_context: bool = True
    ) -> Callable:
        """Decorator for registering tools with automatic enhancements.
        
        Wraps FastMCP.tool() with additional features:
        - Automatic progress tracking context
        - Error handling
        - Response formatting
        """
        def decorator(func: Callable) -> Callable:
            # Get the actual tool name
            tool_name = name or func.__name__
            
            # Create wrapper with progress tracking
            if include_context:
                @asynccontextmanager
                async def with_progress(ctx: Context):
                    """Provide progress tracking context."""
                    tracker = self.progress_tracker.create_tracker(tool_name)
                    ctx.progress = tracker.progress  # type: ignore
                    try:
                        yield ctx
                    finally:
                        await tracker.complete()
                        
                async def wrapped_func(ctx: Context, **kwargs):
                    """Wrapped function with progress tracking."""
                    async with with_progress(ctx):
                        try:
                            return await func(ctx, **kwargs)
                        except Exception as e:
                            logger.error(f"Tool {tool_name} error: {e}")
                            return format_error_response(e)
            else:
                async def wrapped_func(**kwargs):
                    """Wrapped function without context."""
                    try:
                        return await func(**kwargs)
                    except Exception as e:
                        logger.error(f"Tool {tool_name} error: {e}")
                        return format_error_response(e)
                        
            # Register with FastMCP
            wrapped_func.__name__ = tool_name
            if description:
                wrapped_func.__doc__ = description
            else:
                wrapped_func.__doc__ = func.__doc__
                
            return self.mcp.tool()(wrapped_func)
            
        return decorator

    def run(self) -> None:
        """Run the MCP server."""
        logger.info(f"Starting {self.name} v{self.version}")
        self.mcp.run()

    @asynccontextmanager
    async def progress_context(self, operation_name: str):
        """Context manager for progress tracking in operations.
        
        Usage:
            async with self.progress_context("complex_operation") as progress:
                await progress(0.1, "Starting...")
                # ... do work ...
                await progress(0.5, "Halfway there...")
                # ... more work ...
                await progress(1.0, "Complete!")
        """
        tracker = self.progress_tracker.create_tracker(operation_name)
        try:
            yield tracker.progress
        finally:
            await tracker.complete()

    def create_response(
        self,
        success: bool = True,
        data: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None,
        error: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a standardized response.
        
        Shortcut for response_builder methods.
        """
        if success:
            return self.response_builder.success(data, message, **kwargs)
        else:
            return self.response_builder.error(error or "Unknown error", **kwargs)
