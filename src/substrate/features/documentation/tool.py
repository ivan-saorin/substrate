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
    
    # Create handler instance with instance type
    handler = DocumentationHandler(instance_type=INSTANCE_TYPE)
    
    # Register documentation tool with instance-specific name
    @mcp.tool(name=f"{INSTANCE_TYPE}_documentation")
    async def documentation(doc_type: str = "overview") -> Dict[str, Any]:
        """Access system architecture and methodology documentation"""
        try:
            # If doc_type is "overview", use the instance type
            if doc_type == "overview":
                doc_type = INSTANCE_TYPE
                
            result = await handler.get_documentation(doc_type)
            
            # Build suggestions based on doc type
            suggestions = []
            if doc_type == INSTANCE_TYPE:
                # Suggest reading other important docs
                suggestions.extend([
                    response_builder.suggest_next(
                        f"{INSTANCE_TYPE}_documentation",
                        "Read ASR v2.0 - Complete architecture", 
                        doc_type="asr-v2"
                    ),
                    response_builder.suggest_next(
                        f"{INSTANCE_TYPE}_list_docs",
                        "See all available documentation"
                    )
                ])
            
            return result  # Handler already uses response_builder
            
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
            return result  # Handler already uses response_builder
            
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
