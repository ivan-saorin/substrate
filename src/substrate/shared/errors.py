"""Error types for substrate-based MCP servers."""

from typing import List, Optional


class SubstrateError(Exception):
    """Base error for all substrate errors."""
    pass


class ValidationError(SubstrateError):
    """Validation error with field information and suggestions."""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        suggestions: Optional[List[str]] = None
    ):
        super().__init__(message)
        self.field = field
        self.suggestions = suggestions or []
        
    def to_dict(self) -> dict:
        """Convert to dictionary for response."""
        result = {"error": str(self)}
        if self.field:
            result["field"] = self.field
        if self.suggestions:
            result["suggestions"] = self.suggestions
        return result


class NotFoundError(SubstrateError):
    """Resource not found error."""
    
    def __init__(
        self,
        message: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        suggestions: Optional[List[str]] = None
    ):
        """Initialize NotFoundError.
        
        Args:
            message: Error message (used if resource_type/id not provided)
            resource_type: Type of resource (optional)
            resource_id: ID of resource (optional)
            suggestions: Helpful suggestions
        """
        # If resource_type and id provided, construct message
        if resource_type and resource_id:
            message = f"{resource_type} '{resource_id}' not found"
        
        super().__init__(message)
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.suggestions = suggestions or []
        
    def to_dict(self) -> dict:
        """Convert to dictionary for response."""
        result = {"error": str(self)}
        
        if self.resource_type:
            result["resource_type"] = self.resource_type
        if self.resource_id:
            result["resource_id"] = self.resource_id
        if self.suggestions:
            result["suggestions"] = self.suggestions
            
        return result
