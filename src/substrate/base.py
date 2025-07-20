"""Base classes for all MCP servers built on substrate."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
import logging

from fastmcp import FastMCP, Context

from .errors import SubstrateError, ValidationError, NotFoundError
from .components import ResponseBuilder, ProgressTracker, SamplingManager, ReferenceManager

logger = logging.getLogger(__name__)


@dataclass
class ExecutionRequest:
    """Standard execution request format."""
    prompt: str
    model_id: Optional[str] = None  # For blinded execution
    model_name: Optional[str] = None  # For clear execution
    parameters: Dict[str, Any] = None
    constraints: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}
        if self.constraints is None:
            self.constraints = {}


@dataclass
class ExecutionResult:
    """Standard execution result format."""
    response: str
    model_id: Optional[str] = None  # For blinded execution
    model_name: Optional[str] = None  # For clear execution
    metadata: Dict[str, Any] = None
    execution_time: float = 0.0
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    error: Optional[str] = None  # Error message if execution failed
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class HermesExecutor(ABC):
    """Base class for all Hermes execution implementations.
    
    Each MCP server implements its own version based on its needs:
    - BlindedHermes for akab (hides model identities)
    - ClearHermes for synapse (full model access)
    - etc.
    """
    
    @abstractmethod
    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        """Execute a request according to the implementation's rules.
        
        Args:
            request: The execution request
            
        Returns:
            The execution result
        """
        pass


class SubstrateMCP:
    """Base class for all MCP servers built on substrate.
    
    Provides standard functionality:
    - Self-documentation tool
    - Sampling callback tool
    - Response building
    - Progress tracking
    - Error handling
    - Reference management (optional)
    """
    
    def __init__(
        self, 
        name: str, 
        version: str, 
        description: str,
        *,
        instructions: Optional[str] = None,
        enable_references: bool = True
    ):
        """Initialize a substrate-based MCP server.
        
        Args:
            name: Server name (used for tool naming)
            version: Semantic version
            description: Human-readable description
            instructions: Optional usage instructions
            enable_references: Whether to enable reference management
        """
        self.name = name
        self.version = version
        self.description = description
        self.instructions = instructions
        
        # Create FastMCP instance
        self.mcp = FastMCP(f"{name} - {description}")
        
        # Initialize components
        self.response_builder = ResponseBuilder()
        self.progress_tracker = ProgressTracker()
        self.sampling_manager = SamplingManager()
        
        # Add reference manager if enabled
        self.reference_manager = None
        if enable_references:
            self.reference_manager = ReferenceManager(name)
            self._register_reference_tools()
        
        # Register standard tools
        self._register_standard_tools()
        
    def _register_standard_tools(self):
        """Register tools that every substrate server has."""
        
        # Self-documentation tool (NO ctx parameter - cleaner!)
        @self.mcp.tool(name=self.name)
        async def self_documentation() -> Dict[str, Any]:
            """Get server capabilities and documentation."""
            try:
                capabilities = await self.get_capabilities()
                
                response_data = {
                    "name": self.name,
                    "version": self.version,
                    "description": self.description,
                    "capabilities": capabilities
                }
                
                if self.instructions:
                    response_data["instructions"] = self.instructions
                    
                return self.create_response(
                    success=True,
                    data=response_data
                )
            except Exception as e:
                logger.error(f"Error in self-documentation: {e}")
                return self.create_response(
                    success=False,
                    error=str(e)
                )
        
        # Sampling callback tool
        @self.mcp.tool(name=f"{self.name}_sampling_callback")
        async def sampling_callback(
            request_id: str,
            response: str
        ) -> Dict[str, Any]:
            """Handle sampling callback responses."""
            try:
                result = await self.sampling_manager.handle_callback(
                    request_id,
                    response
                )
                
                return self.create_response(
                    success=True,
                    data=result
                )
            except Exception as e:
                logger.error(f"Error in sampling callback: {e}")
                return self.create_response(
                    success=False,
                    error=str(e)
                )
    
    def _register_reference_tools(self):
        """Register reference management tools."""
        
        @self.mcp.tool(name=f"{self.name}_create_ref")
        async def create_ref(ref: str, content: str, 
                           metadata: Optional[Dict] = None) -> Dict[str, Any]:
            """Create or update a reference."""
            try:
                result = await self.reference_manager.create_ref(ref, content, metadata)
                return self.create_response(success=True, data=result)
            except Exception as e:
                return self.create_response(success=False, error=str(e))
        
        @self.mcp.tool(name=f"{self.name}_read_ref")
        async def read_ref(ref: str) -> Dict[str, Any]:
            """Read reference content."""
            try:
                content = await self.reference_manager.read_ref(ref)
                return self.create_response(
                    success=True, 
                    data={"ref": ref, "content": content}
                )
            except Exception as e:
                return self.create_response(success=False, error=str(e))
        
        @self.mcp.tool(name=f"{self.name}_update_ref")
        async def update_ref(ref: str, content: str) -> Dict[str, Any]:
            """Update existing reference."""
            try:
                result = await self.reference_manager.update_ref(ref, content)
                return self.create_response(success=True, data=result)
            except Exception as e:
                return self.create_response(success=False, error=str(e))
        
        @self.mcp.tool(name=f"{self.name}_delete_ref")
        async def delete_ref(ref: str) -> Dict[str, Any]:
            """Delete a reference."""
            try:
                result = await self.reference_manager.delete_ref(ref)
                return self.create_response(success=True, data=result)
            except Exception as e:
                return self.create_response(success=False, error=str(e))
        
        @self.mcp.tool(name=f"{self.name}_list_refs")
        async def list_refs(prefix: Optional[str] = None) -> Dict[str, Any]:
            """List all references with optional prefix filter."""
            try:
                refs = await self.reference_manager.list_refs(prefix)
                return self.create_response(
                    success=True,
                    data={"refs": refs, "count": len(refs)}
                )
            except Exception as e:
                return self.create_response(success=False, error=str(e))
    
    @abstractmethod
    async def get_capabilities(self) -> Dict[str, Any]:
        """Return server capabilities for self-documentation.
        
        Must be implemented by each server.
        """
        pass
    
    def tool(self, **kwargs):
        """Decorator to register a tool with the MCP server."""
        return self.mcp.tool(**kwargs)
    
    def run(self):
        """Run the MCP server."""
        self.mcp.run()
    
    def create_response(
        self,
        success: bool = True,
        data: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None,
        error: Optional[str] = None,
        multi_turn: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a standardized response.
        
        Args:
            success: Whether the operation succeeded
            data: Response data
            message: Human-readable message
            error: Error message if success=False
            multi_turn: Multi-turn conversation metadata
            **kwargs: Additional fields
            
        Returns:
            Standardized response dict
        """
        response = self.response_builder.create(
            success=success,
            data=data,
            message=message,
            error=error,
            **kwargs
        )
        
        # Add multi-turn support if provided
        if multi_turn:
            response["multi_turn"] = multi_turn
            
        return response
    
    def create_error_response(
        self,
        error: str,
        error_type: str = "general",
        suggestions: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a standardized error response.
        
        Args:
            error: Error message
            error_type: Type of error
            suggestions: Helpful suggestions
            **kwargs: Additional fields
            
        Returns:
            Standardized error response
        """
        return self.response_builder.error(
            error=error,
            error_type=error_type,
            suggestions=suggestions,
            **kwargs
        )
    
    async def _compose_input(self, prompt: str = None, ref: str = None,
                           refs: List[str] = None, prompt_ref: str = None) -> str:
        """Standard input composition - same logic everywhere.
        
        Priority: ref > refs > prompt_ref > prompt
        """
        if ref:
            return await self.reference_manager.read_ref(ref)
        elif refs:
            parts = []
            for r in refs:
                parts.append(await self.reference_manager.read_ref(r))
            return "\n\n".join(parts)
        elif prompt_ref:
            return await self.reference_manager.read_ref(prompt_ref)
        elif prompt:
            return prompt
        else:
            raise ValueError("No input provided")
    
    def progress_context(self, operation_name: str):
        """Create a progress tracking context.
        
        Usage:
            async with self.progress_context("my_operation") as progress:
                await progress(0.1, "Starting...")
                # ... do work ...
                await progress(0.5, "Halfway done...")
                # ... more work ...
                await progress(1.0, "Complete!")
        """
        return self.progress_tracker.create_context(operation_name)
