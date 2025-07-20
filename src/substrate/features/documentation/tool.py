"""
Documentation feature - Tool registration
"""
import logging
from typing import Dict, Any, List
from .handler import DocumentationHandler

logger = logging.getLogger(__name__)


def register_documentation_tools(mcp) -> List[dict]:
    """
    Register documentation tools with FastMCP
    
    Args:
        mcp: FastMCP instance to register tools on
        
    Returns:
        List of tool metadata
    """
    # Import shared instances inside function to avoid circular imports
    from ...shared.instances import response_builder, INSTANCE_TYPE
    
    # Create handler instance
    handler = DocumentationHandler()
    
    # Register documentation tool with instance-specific name
    @mcp.tool(name=f"{INSTANCE_TYPE}_documentation")
    async def documentation(doc_type: str = "overview") -> Dict[str, Any]:
        """Access system architecture and methodology documentation"""
        try:
            result = await handler.get_documentation(doc_type)
            
            # Build suggestions based on doc type
            suggestions = []
            if doc_type == "overview":
                suggestions.append(
                    response_builder.suggest_next(
                        f"{INSTANCE_TYPE}_documentation",
                        "Read ASR v2.0 - Complete architecture", 
                        doc_type="asr-v2"
                    )
                )
            
            return response_builder.success(
                data=result,
                message=f"Loaded {doc_type} documentation",
                suggestions=suggestions
            )
            
        except Exception as e:
            logger.error(f"Error in {INSTANCE_TYPE}_documentation: {e}", exc_info=True)
            return response_builder.error(
                error=str(e),
                details={"doc_type": doc_type}
            )
    
    # Register list_documentation tool with instance-specific name
    @mcp.tool(name=f"{INSTANCE_TYPE}_list_docs")
    async def list_docs() -> Dict[str, Any]:
        """List all available documentation"""
        try:
            result = await handler.list_documentation()
            
            return response_builder.success(
                data=result,
                message=f"Found {result['count']} documentation files"
            )
            
        except Exception as e:
            logger.error(f"Error in {INSTANCE_TYPE}_list_docs: {e}", exc_info=True)
            return response_builder.error(error=str(e))
    
    # Return tool metadata for discovery
    return [
        {
            "name": f"{INSTANCE_TYPE}_documentation",
            "description": "Access system architecture and methodology documentation"
        },
        {
            "name": f"{INSTANCE_TYPE}_list_docs",
            "description": "List all available documentation"
        }
    ]
