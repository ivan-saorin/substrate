"""
References feature - Business logic handler
"""
import logging
from typing import Dict, Any, Optional, List
from ...shared.instances import reference_manager

logger = logging.getLogger(__name__)


class ReferenceHandler:
    """Handles reference CRUD operations"""
    
    def __init__(self):
        self.storage = reference_manager
        logger.info("ReferenceHandler initialized")
    
    async def create_reference(self, ref: str, content: str, 
                             metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create or update a reference
        
        Args:
            ref: Reference path (e.g., 'prompts/enhanced')
            content: Content to store
            metadata: Optional metadata
            
        Returns:
            Dict with creation status and details
        """
        try:
            result = await self.storage.create_ref(ref, content, metadata)
            logger.info(f"Reference '{ref}' {'created' if result['created'] else 'updated'}")
            return result
            
        except Exception as e:
            logger.error(f"Error creating reference {ref}: {e}", exc_info=True)
            raise
    
    async def read_reference(self, ref: str) -> str:
        """
        Read reference content
        
        Args:
            ref: Reference path
            
        Returns:
            Reference content
        """
        try:
            content = await self.storage.read_ref(ref)
            logger.info(f"Reference '{ref}' read successfully")
            return content
            
        except Exception as e:
            logger.error(f"Error reading reference {ref}: {e}", exc_info=True)
            raise
    
    async def update_reference(self, ref: str, content: str) -> Dict[str, Any]:
        """
        Update existing reference
        
        Args:
            ref: Reference path
            content: New content
            
        Returns:
            Dict with update status
        """
        try:
            result = await self.storage.update_ref(ref, content)
            logger.info(f"Reference '{ref}' updated")
            return result
            
        except Exception as e:
            logger.error(f"Error updating reference {ref}: {e}", exc_info=True)
            raise
    
    async def delete_reference(self, ref: str) -> Dict[str, Any]:
        """
        Delete a reference
        
        Args:
            ref: Reference path
            
        Returns:
            Dict with deletion status
        """
        try:
            result = await self.storage.delete_ref(ref)
            logger.info(f"Reference '{ref}' deleted")
            return result
            
        except Exception as e:
            logger.error(f"Error deleting reference {ref}: {e}", exc_info=True)
            raise
    
    async def list_references(self, prefix: Optional[str] = None) -> List[str]:
        """
        List all references with optional prefix filter
        
        Args:
            prefix: Optional prefix to filter references
            
        Returns:
            List of reference paths
        """
        try:
            refs = await self.storage.list_refs(prefix)
            logger.info(f"Listed {len(refs)} references" + 
                       (f" with prefix '{prefix}'" if prefix else ""))
            return refs
            
        except Exception as e:
            logger.error(f"Error listing references: {e}", exc_info=True)
            raise
    
    def suggest_next_actions(self, ref: str, operation: str) -> List[Dict[str, Any]]:
        """
        Generate suggestions for next actions based on reference and operation
        
        Args:
            ref: Reference path
            operation: Operation performed (create, read, update, delete)
            
        Returns:
            List of suggestion dictionaries
        """
        suggestions = []
        
        if operation in ['create', 'update']:
            # Suggest reading the reference
            suggestions.append({
                "tool": "read_ref",
                "reason": "Read the saved reference",
                "params": {"ref": ref}
            })
            
            # Suggest listing related references
            if '/' in ref:
                prefix = ref.split('/')[0]
                suggestions.append({
                    "tool": "list_refs",
                    "reason": f"View all {prefix} references",
                    "params": {"prefix": prefix}
                })
            
            # Context-specific suggestions
            if 'prompt' in ref.lower():
                suggestions.append({
                    "tool": "synapse:enhance_prompt",
                    "reason": "Enhance the saved prompt",
                    "params": {"prompt_ref": ref}
                })
            
        elif operation == 'read':
            # Suggest updating
            suggestions.append({
                "tool": "update_ref",
                "reason": "Update reference content",
                "params": {"ref": ref}
            })
            
            # Suggest execution if appropriate
            suggestions.append({
                "tool": "execute",
                "reason": "Execute as pattern",
                "params": {"ref": ref}
            })
            
        elif operation == 'list':
            if prefix and '/' not in prefix:
                # Suggest drilling down
                suggestions.append({
                    "tool": "list_refs",
                    "reason": f"View sub-categories",
                    "params": {"prefix": f"{prefix}/"}
                })
        
        return suggestions
