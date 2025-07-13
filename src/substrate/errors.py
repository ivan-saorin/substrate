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
        resource_type: str,
        resource_id: str,
        suggestions: Optional[List[str]] = None
    ):
        message = f"{resource_type} '{resource_id}' not found"
        super().__init__(message)
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.suggestions = suggestions or []
        
    def to_dict(self) -> dict:
        """Convert to dictionary for response."""
        result = {
            "error": str(self),
            "resource_type": self.resource_type,
            "resource_id": self.resource_id
        }
        if self.suggestions:
            result["suggestions"] = self.suggestions
        return result
