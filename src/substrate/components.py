"""Shared components for substrate-based MCP servers."""

import time
import uuid
import logging
from typing import Any, Dict, List, Optional, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class ResponseBuilder:
    """Builds standardized responses."""
    
    def success(
        self,
        data: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Build a success response."""
        response = {
            "success": True,
            "timestamp": time.time()
        }
        
        if data is not None:
            response["data"] = data
            
        if message:
            response["message"] = message
            
        # Add any additional fields
        response.update(kwargs)
        
        return response
    
    def error(
        self,
        error: str,
        suggestions: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Build an error response."""
        response = {
            "success": False,
            "error": error,
            "timestamp": time.time()
        }
        
        if suggestions:
            response["suggestions"] = suggestions
            
        # Add any additional fields
        response.update(kwargs)
        
        return response
    
    def paginated(
        self,
        items: List[Any],
        page: int = 1,
        page_size: int = 10,
        total: Optional[int] = None,
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Build a paginated response."""
        data = {
            "items": items,
            "page": page,
            "page_size": page_size,
            "count": len(items)
        }
        
        if total is not None:
            data["total"] = total
            data["total_pages"] = (total + page_size - 1) // page_size
            
        return self.success(data, message)
    
    def comparison_result(
        self,
        results: List[Any],
        winner: Optional[str] = None,
        metrics: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Build a comparison result response."""
        data = {"results": results}
        
        if winner:
            data["winner"] = winner
            
        if metrics:
            data["metrics"] = metrics
            
        return self.success(data, message, **kwargs)


class ProgressTracker:
    """Tracks progress of long-running operations."""
    
    def __init__(self):
        self._operations = {}
    
    @asynccontextmanager
    async def create_context(self, operation_name: str):
        """Create a progress tracking context."""
        operation_id = str(uuid.uuid4())
        
        self._operations[operation_id] = {
            "name": operation_name,
            "progress": 0.0,
            "status": "running",
            "start_time": time.time()
        }
        
        async def update_progress(progress: float, status: str):
            """Update progress for this operation."""
            if operation_id in self._operations:
                self._operations[operation_id]["progress"] = progress
                self._operations[operation_id]["status"] = status
                logger.debug(f"{operation_name}: {progress:.0%} - {status}")
        
        try:
            yield update_progress
        finally:
            # Clean up operation
            if operation_id in self._operations:
                self._operations[operation_id]["status"] = "completed"
                self._operations[operation_id]["progress"] = 1.0


class SamplingManager:
    """Manages sampling requests and callbacks."""
    
    def __init__(self):
        self._pending_requests = {}
    
    def should_request_sampling(self, context: str) -> bool:
        """Check if we should request sampling for this context."""
        # Basic heuristic - can be overridden
        return context in ["help", "constraints", "clarification"]
    
    def create_request(
        self,
        prompt: str,
        context: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a sampling request."""
        request_id = str(uuid.uuid4())
        
        request = {
            "id": request_id,
            "prompt": prompt,
            "instruction": f"Please process and respond with request_id='{request_id}'"
        }
        
        if context:
            request["context"] = context
            
        # Store for later callback
        self._pending_requests[request_id] = {
            "prompt": prompt,
            "context": context,
            "created_at": time.time(),
            **kwargs
        }
        
        return request
    
    async def handle_callback(
        self,
        request_id: str,
        response: str
    ) -> Dict[str, Any]:
        """Handle a sampling callback."""
        if request_id not in self._pending_requests:
            logger.warning(f"Unknown sampling request: {request_id}")
            return {"processed": False, "error": "Unknown request ID"}
        
        request = self._pending_requests.pop(request_id)
        
        return {
            "processed": True,
            "original_request": request,
            "response": response,
            "processing_time": time.time() - request["created_at"]
        }
    
    async def cleanup_old_requests(self, max_age_seconds: float = 300):
        """Clean up old pending requests."""
        current_time = time.time()
        expired = []
        
        for request_id, request in self._pending_requests.items():
            if current_time - request["created_at"] > max_age_seconds:
                expired.append(request_id)
        
        for request_id in expired:
            self._pending_requests.pop(request_id)
            
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired sampling requests")
