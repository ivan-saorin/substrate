"""Reference management feature - CRUD operations for references"""
from typing import Dict, Any, List, Optional


def register_reference_tools(server) -> List[dict]:
    """Register reference management tools on the server"""
    
    async def create_ref(
        ref: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create or update a reference
        
        Args:
            ref: Reference path (e.g., 'prompts/enhanced')
            content: Content to store
            metadata: Optional metadata
        """
        try:
            result = await server.reference_manager.create_ref(ref, content, metadata)
            
            suggestions = [
                server.response_builder.suggest_next(
                    f"{server.instance_type}:read_ref",
                    "Read the saved reference",
                    ref=ref
                ),
                server.response_builder.suggest_next(
                    f"{server.instance_type}:list_refs", 
                    "View all references",
                    prefix=ref.split('/')[0] if '/' in ref else None
                )
            ]
            
            if 'prompt' in ref.lower():
                suggestions.append(
                    server.response_builder.suggest_next(
                        "synapse:enhance_prompt",
                        "Enhance the saved prompt",
                        prompt_ref=ref
                    )
                )
            
            return server.response_builder.success(
                data=result,
                message=f"Reference {'created' if result['created'] else 'updated'}: {ref}",
                suggestions=suggestions
            )
            
        except Exception as e:
            return server.response_builder.error(
                str(e),
                details={"ref": ref}
            )
    
    async def read_ref(ref: str) -> Dict[str, Any]:
        """Read reference content
        
        Args:
            ref: Reference path to read
        """
        try:
            content = await server.reference_manager.read_ref(ref)
            
            suggestions = [
                server.response_builder.suggest_next(
                    f"{server.instance_type}:update_ref",
                    "Update this reference",
                    ref=ref
                )
            ]
            
            # Context-aware suggestions
            if 'prompt' in ref.lower():
                suggestions.extend([
                    server.response_builder.suggest_next(
                        "synapse:enhance_prompt",
                        "Enhance this prompt",
                        prompt_ref=ref
                    ),
                    server.response_builder.suggest_next(
                        "akab:quick_compare",
                        "Compare across providers",
                        prompt=content
                    )
                ])
            elif server.instance_type == 'tloen':
                suggestions.append(
                    server.response_builder.suggest_next(
                        f"{server.instance_type}:execute",
                        "Apply this template",
                        ref=ref
                    )
                )
            
            return server.response_builder.success(
                data={"content": content, "ref": ref},
                message=f"Reference loaded: {ref}",
                suggestions=suggestions
            )
            
        except FileNotFoundError:
            return server.response_builder.error(
                f"Reference not found: {ref}",
                details={"ref": ref, "type": "not_found"}
            )
        except Exception as e:
            return server.response_builder.error(str(e))
    
    async def update_ref(ref: str, content: str) -> Dict[str, Any]:
        """Update existing reference
        
        Args:
            ref: Reference path to update
            content: New content
        """
        try:
            result = await server.reference_manager.update_ref(ref, content)
            
            return server.response_builder.success(
                data=result,
                message=f"Reference updated: {ref}",
                suggestions=[
                    server.response_builder.suggest_next(
                        f"{server.instance_type}:read_ref",
                        "Read updated reference",
                        ref=ref
                    )
                ]
            )
            
        except FileNotFoundError:
            return server.response_builder.error(
                f"Reference not found: {ref}",
                details={"ref": ref, "hint": "Use create_ref for new references"}
            )
        except Exception as e:
            return server.response_builder.error(str(e))
    
    async def delete_ref(ref: str) -> Dict[str, Any]:
        """Delete a reference
        
        Args:
            ref: Reference path to delete
        """
        try:
            result = await server.reference_manager.delete_ref(ref)
            
            return server.response_builder.success(
                data=result,
                message=f"Reference deleted: {ref}",
                suggestions=[
                    server.response_builder.suggest_next(
                        f"{server.instance_type}:list_refs",
                        "View remaining references"
                    )
                ]
            )
            
        except FileNotFoundError:
            return server.response_builder.error(
                f"Reference not found: {ref}",
                details={"ref": ref}
            )
        except Exception as e:
            return server.response_builder.error(str(e))
    
    async def list_refs(prefix: Optional[str] = None) -> Dict[str, Any]:
        """List all references
        
        Args:
            prefix: Optional prefix to filter references
        """
        try:
            refs = await server.reference_manager.list_refs(prefix)
            
            suggestions = []
            if refs:
                # Suggest reading the first few
                for ref in refs[:3]:
                    suggestions.append(
                        server.response_builder.suggest_next(
                            f"{server.instance_type}:read_ref",
                            f"Read {ref}",
                            ref=ref
                        )
                    )
            
            return server.response_builder.success(
                data={
                    "refs": refs,
                    "count": len(refs),
                    "prefix": prefix
                },
                message=f"Found {len(refs)} references",
                suggestions=suggestions
            )
            
        except Exception as e:
            return server.response_builder.error(str(e))
    
    # Register all reference tools
    server.register_tool(f"{server.instance_type}_create_ref", create_ref)
    server.register_tool(f"{server.instance_type}_read_ref", read_ref)
    server.register_tool(f"{server.instance_type}_update_ref", update_ref)
    server.register_tool(f"{server.instance_type}_delete_ref", delete_ref)
    server.register_tool(f"{server.instance_type}_list_refs", list_refs)
    
    # Return tool metadata
    tools = []
    for name in ['create_ref', 'read_ref', 'update_ref', 'delete_ref', 'list_refs']:
        tools.append({
            "name": f"{server.instance_type}_{name}",
            "description": f"Reference management: {name}"
        })
    
    return tools
