"""Response formatting utilities for Substrate MCP servers."""

import time
from typing import Any, Dict, List, Optional, Union

from .types import Annotation, ResponseMetadata


class ResponseBuilder:
    """Builds standardized responses for MCP servers.
    
    Ensures consistent response format across all Substrate-based servers.
    """
    
    def __init__(self):
        """Initialize the response builder."""
        self._default_annotations = {
            "priority": 0.5,
            "audience": ["user", "assistant"]
        }
    
    def success(
        self,
        data: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None,
        *,
        annotations: Optional[Annotation] = None,
        metadata: Optional[ResponseMetadata] = None,
        **extra_fields
    ) -> Dict[str, Any]:
        """Build a success response.
        
        Args:
            data: Response data payload
            message: Human-readable success message
            annotations: Optional annotation metadata
            metadata: Optional response metadata
            **extra_fields: Additional fields (e.g., _sampling_request)
            
        Returns:
            Standardized success response dict
        """
        response = {
            "success": True,
            "timestamp": time.time(),
        }
        
        if data is not None:
            response["data"] = data
            
        if message:
            response["message"] = message
            
        # Add annotations if provided
        if annotations:
            response["_annotations"] = self._format_annotations(annotations)
            
        # Add metadata if provided
        if metadata:
            response["_metadata"] = metadata
            
        # Add any extra fields (like _sampling_request)
        response.update(extra_fields)
        
        return response
    
    def error(
        self,
        error: str,
        *,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
        **extra_fields
    ) -> Dict[str, Any]:
        """Build an error response.
        
        Args:
            error: Error message
            error_code: Optional error code
            details: Optional error details
            suggestions: Optional suggestions for fixing
            **extra_fields: Additional fields
            
        Returns:
            Standardized error response dict
        """
        response = {
            "success": False,
            "error": error,
            "timestamp": time.time(),
        }
        
        if error_code:
            response["error_code"] = error_code
            
        if details:
            response["details"] = details
            
        if suggestions:
            response["suggestions"] = suggestions
            
        response.update(extra_fields)
        
        return response
    
    def _format_annotations(self, annotation: Annotation) -> Dict[str, Any]:
        """Format annotation data for response.
        
        Args:
            annotation: Annotation data
            
        Returns:
            Formatted annotation dict
        """
        if isinstance(annotation, dict):
            # Merge with defaults
            formatted = self._default_annotations.copy()
            formatted.update(annotation)
            return formatted
        else:
            # Assume it's already properly formatted
            return annotation
    
    def with_progress(
        self,
        response: Dict[str, Any],
        progress: float,
        status: str
    ) -> Dict[str, Any]:
        """Add progress information to a response.
        
        Args:
            response: Base response dict
            progress: Progress value (0.0 to 1.0)
            status: Current status message
            
        Returns:
            Response with progress information
        """
        response["_progress"] = {
            "value": max(0.0, min(1.0, progress)),
            "status": status,
            "timestamp": time.time()
        }
        return response
    
    def paginated(
        self,
        items: List[Any],
        *,
        page: int = 1,
        page_size: int = 10,
        total: Optional[int] = None,
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Build a paginated response.
        
        Args:
            items: List of items for current page
            page: Current page number (1-indexed)
            page_size: Items per page
            total: Total number of items (if known)
            message: Optional message
            
        Returns:
            Paginated response dict
        """
        if total is None:
            total = len(items)
            
        total_pages = (total + page_size - 1) // page_size
        
        pagination = {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
        
        return self.success(
            data={
                "items": items,
                "pagination": pagination
            },
            message=message
        )
    
    def file_response(
        self,
        content: Union[str, bytes],
        filename: str,
        *,
        mime_type: str = "text/plain",
        encoding: Optional[str] = None,
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Build a response containing file data.
        
        Args:
            content: File content
            filename: Name of the file
            mime_type: MIME type
            encoding: Optional encoding (for text files)
            message: Optional message
            
        Returns:
            File response dict
        """
        data = {
            "filename": filename,
            "mime_type": mime_type,
            "size": len(content),
        }
        
        if encoding:
            data["encoding"] = encoding
            
        if isinstance(content, bytes):
            # For binary content, we'd typically base64 encode
            # but for now just indicate it's binary
            data["is_binary"] = True
            data["content"] = content.decode("utf-8", errors="replace")
        else:
            data["content"] = content
            
        return self.success(data=data, message=message)
    
    def comparison_result(
        self,
        results: List[Dict[str, Any]],
        *,
        winner: Optional[str] = None,
        metrics: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Build a comparison result response (for AKAB).
        
        Args:
            results: List of comparison results
            winner: Optional winner identifier
            metrics: Optional comparison metrics
            message: Optional message
            
        Returns:
            Comparison response dict
        """
        data = {
            "results": results,
            "comparison_count": len(results)
        }
        
        if winner:
            data["winner"] = winner
            
        if metrics:
            data["metrics"] = metrics
            
        return self.success(data=data, message=message)
