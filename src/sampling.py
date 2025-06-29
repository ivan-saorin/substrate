"""Sampling emulation for Claude Desktop.

Since Claude Desktop doesn't support native sampling, we emulate it
by injecting _sampling_request in tool responses and handling callbacks.
"""

import asyncio
import logging
import time
import uuid
from typing import Any, Callable, Dict, Optional, Set

from .types import SamplingRequest

logger = logging.getLogger(__name__)


class SamplingManager:
    """Manages sampling requests and responses for Claude Desktop.
    
    Emulates MCP sampling by:
    1. Injecting _sampling_request in tool responses
    2. Tracking pending requests
    3. Processing callbacks when the client responds
    """
    
    def __init__(self, callback_tool_prefix: str = ""):
        """Initialize the sampling manager.
        
        Args:
            callback_tool_prefix: Prefix for callback tool (e.g., "akab")
        """
        self.callback_tool_prefix = callback_tool_prefix
        self._pending_requests: Dict[str, SamplingRequest] = {}
        self._request_handlers: Dict[str, Callable] = {}
        self._request_timeouts: Dict[str, float] = {}
        
        # Start cleanup task
        self._cleanup_task = asyncio.create_task(self._cleanup_expired())
        
    def should_request_sampling(self, context: str) -> bool:
        """Determine if we should request sampling for this context.
        
        Args:
            context: Context of the current operation
            
        Returns:
            Whether to request sampling
        """
        # Heuristics for when to request sampling
        sampling_contexts = {
            "help": True,  # User asking for help
            "constraints": True,  # Need constraint suggestions
            "clarification": True,  # Need clarification
            "options": True,  # Need to present options
            "error_recovery": True,  # Help recovering from errors
        }
        
        return sampling_contexts.get(context, False)
    
    def create_request(
        self,
        prompt: str,
        *,
        max_tokens: int = 100,
        temperature: float = 0.7,
        context: Optional[Dict[str, Any]] = None,
        handler: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Create a sampling request to inject in response.
        
        Args:
            prompt: The prompt to send to the LLM
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            context: Optional context data
            handler: Optional handler for the response
            
        Returns:
            Sampling request dict to inject as _sampling_request
        """
        request_id = str(uuid.uuid4())
        callback_tool = f"{self.callback_tool_prefix}_sampling_callback"
        
        request = SamplingRequest(
            id=request_id,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            callback_tool=callback_tool,
            context=context
        )
        
        # Track the request
        self._pending_requests[request_id] = request
        self._request_timeouts[request_id] = time.time() + 300  # 5 min timeout
        
        if handler:
            self._request_handlers[request_id] = handler
            
        logger.debug(f"Created sampling request {request_id}")
        
        # Return dict format for injection
        return {
            "id": request_id,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "instruction": (
                f"Please process this request and call {callback_tool} "
                f"with request_id='{request_id}' and your response."
            )
        }
    
    async def handle_response(
        self,
        request_id: str,
        response: str
    ) -> Dict[str, Any]:
        """Handle a sampling response callback.
        
        Args:
            request_id: ID of the original request
            response: The LLM's response
            
        Returns:
            Result of processing the response
        """
        if request_id not in self._pending_requests:
            logger.warning(f"Unknown sampling request: {request_id}")
            return {
                "processed": False,
                "error": "Unknown request ID"
            }
            
        request = self._pending_requests.pop(request_id)
        self._request_timeouts.pop(request_id, None)
        
        result = {
            "request_id": request_id,
            "original_prompt": request.prompt,
            "response": response,
            "context": request.context
        }
        
        # Call handler if registered
        if request_id in self._request_handlers:
            handler = self._request_handlers.pop(request_id)
            try:
                handler_result = await handler(response, request.context)
                result["handler_result"] = handler_result
            except Exception as e:
                logger.error(f"Sampling handler error: {e}")
                result["handler_error"] = str(e)
                
        logger.debug(f"Processed sampling response for {request_id}")
        return result
    
    async def _cleanup_expired(self) -> None:
        """Background task to clean up expired requests."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                now = time.time()
                expired = [
                    req_id for req_id, timeout in self._request_timeouts.items()
                    if now > timeout
                ]
                
                for req_id in expired:
                    logger.warning(f"Sampling request {req_id} expired")
                    self._pending_requests.pop(req_id, None)
                    self._request_timeouts.pop(req_id, None)
                    self._request_handlers.pop(req_id, None)
                    
            except Exception as e:
                logger.error(f"Cleanup task error: {e}")
                
    def get_pending_count(self) -> int:
        """Get count of pending sampling requests."""
        return len(self._pending_requests)
    
    def clear_all(self) -> None:
        """Clear all pending requests."""
        self._pending_requests.clear()
        self._request_handlers.clear()
        self._request_timeouts.clear()
        
    async def close(self) -> None:
        """Clean up resources."""
        self._cleanup_task.cancel()
        try:
            await self._cleanup_task
        except asyncio.CancelledError:
            pass
        self.clear_all()


class SamplingContext:
    """Context manager for sampling operations.
    
    Usage:
        async with SamplingContext(manager, "help") as ctx:
            if ctx.should_sample:
                ctx.request = manager.create_request("What would help?")
            # ... do work ...
            response["_sampling_request"] = ctx.request
    """
    
    def __init__(self, manager: SamplingManager, context: str):
        """Initialize sampling context.
        
        Args:
            manager: The sampling manager
            context: Context for this operation
        """
        self.manager = manager
        self.context = context
        self.should_sample = manager.should_request_sampling(context)
        self.request: Optional[Dict[str, Any]] = None
        
    async def __aenter__(self):
        """Enter the context."""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the context."""
        # Could add cleanup here if needed
        pass
