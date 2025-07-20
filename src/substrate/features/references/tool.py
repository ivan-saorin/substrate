"""
Reference management feature - Tool registration
"""
import logging
from typing import Dict, Any, List, Optional
from .handler import ReferenceHandler

logger = logging.getLogger(__name__)


def register_reference_tools(mcp) -> List[dict]:
    """
    Register reference management tools with FastMCP
    
    Args:
        mcp: FastMCP instance to register tools on
        
    Returns:
        List of tool metadata
    """
    # Import shared instances
    from ...shared.instances import response_builder, INSTANCE_TYPE
    
    # Create handler instance
    handler = ReferenceHandler()
    
    # Create reference tool
    @mcp.tool(name=f"{INSTANCE_TYPE}_create_ref")
    async def create_ref(
        ref: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create or update a reference"""
        try:
            result = await handler.create_reference(ref, content, metadata)
            
            # Generate smart suggestions
            suggestions = [
                response_builder.suggest_next(
                    f"{INSTANCE_TYPE}_read_ref",
                    "Read the saved reference",
                    ref=ref
                )
            ]
            
            # Add context-aware suggestions
            handler_suggestions = handler.suggest_next_actions(ref, 'create')
            for suggestion in handler_suggestions:
                suggestions.append(
                    response_builder.suggest_next(
                        suggestion['tool'],
                        suggestion['reason'],
                        **suggestion['params']
                    )
                )
            
            return response_builder.success(
                data=result,
                message=f"Reference '{ref}' {'created' if result['created'] else 'updated'}",
                suggestions=suggestions[:3]  # Limit to top 3
            )
            
        except Exception as e:
            logger.error(f"Error in create_ref: {e}", exc_info=True)
            return response_builder.error(
                error=str(e),
                details={"ref": ref}
            )
    
    # Read reference tool
    @mcp.tool(name=f"{INSTANCE_TYPE}_read_ref")
    async def read_ref(ref: str) -> Dict[str, Any]:
        """Read reference content"""
        try:
            content = await handler.read_reference(ref)
            
            # Generate suggestions based on content
            suggestions = []
            handler_suggestions = handler.suggest_next_actions(ref, 'read')
            for suggestion in handler_suggestions:
                suggestions.append(
                    response_builder.suggest_next(
                        suggestion['tool'],
                        suggestion['reason'],
                        **suggestion['params']
                    )
                )
            
            return response_builder.success(
                data={"ref": ref, "content": content},
                message=f"Reference '{ref}' loaded",
                suggestions=suggestions[:3]
            )
            
        except Exception as e:
            logger.error(f"Error in read_ref: {e}", exc_info=True)
            return response_builder.error(
                error=f"Reference not found: {ref}",
                details={"ref": ref}
            )
    
    # Update reference tool
    @mcp.tool(name=f"{INSTANCE_TYPE}_update_ref")
    async def update_ref(ref: str, content: str) -> Dict[str, Any]:
        """Update existing reference"""
        try:
            result = await handler.update_reference(ref, content)
            
            suggestions = [
                response_builder.suggest_next(
                    f"{INSTANCE_TYPE}_read_ref",
                    "Read the updated reference",
                    ref=ref
                )
            ]
            
            return response_builder.success(
                data=result,
                message=f"Reference '{ref}' updated",
                suggestions=suggestions
            )
            
        except Exception as e:
            logger.error(f"Error in update_ref: {e}", exc_info=True)
            return response_builder.error(
                error=str(e),
                details={"ref": ref}
            )
    
    # Delete reference tool
    @mcp.tool(name=f"{INSTANCE_TYPE}_delete_ref")
    async def delete_ref(ref: str) -> Dict[str, Any]:
        """Delete a reference"""
        try:
            result = await handler.delete_reference(ref)
            
            suggestions = [
                response_builder.suggest_next(
                    f"{INSTANCE_TYPE}_list_refs",
                    "View remaining references"
                )
            ]
            
            return response_builder.success(
                data=result,
                message=f"Reference '{ref}' deleted",
                suggestions=suggestions
            )
            
        except Exception as e:
            logger.error(f"Error in delete_ref: {e}", exc_info=True)
            return response_builder.error(
                error=str(e),
                details={"ref": ref}
            )
    
    # List references tool
    @mcp.tool(name=f"{INSTANCE_TYPE}_list_refs")
    async def list_refs(prefix: Optional[str] = None) -> Dict[str, Any]:
        """List all references with optional prefix filter"""
        try:
            refs = await handler.list_references(prefix)
            
            suggestions = []
            if refs and not prefix:
                # Suggest exploring categories
                categories = set(ref.split('/')[0] for ref in refs if '/' in ref)
                for category in list(categories)[:3]:
                    suggestions.append(
                        response_builder.suggest_next(
                            f"{INSTANCE_TYPE}_list_refs",
                            f"View {category} references",
                            prefix=category
                        )
                    )
            
            return response_builder.success(
                data={"refs": refs, "count": len(refs)},
                message=f"Found {len(refs)} references",
                suggestions=suggestions
            )
            
        except Exception as e:
            logger.error(f"Error in list_refs: {e}", exc_info=True)
            return response_builder.error(error=str(e))
    
    # Return tool metadata
    return [
        {
            "name": f"{INSTANCE_TYPE}_create_ref",
            "description": "Create or update a reference"
        },
        {
            "name": f"{INSTANCE_TYPE}_read_ref", 
            "description": "Read reference content"
        },
        {
            "name": f"{INSTANCE_TYPE}_update_ref",
            "description": "Update existing reference"
        },
        {
            "name": f"{INSTANCE_TYPE}_delete_ref",
            "description": "Delete a reference"
        },
        {
            "name": f"{INSTANCE_TYPE}_list_refs",
            "description": "List all references with optional prefix filter"
        }
    ]
