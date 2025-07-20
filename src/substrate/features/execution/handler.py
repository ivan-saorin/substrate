"""
Execution feature - Business logic handler
"""
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class ExecutionHandler:
    """Handles pattern execution for TLOEN/UQBAR instances"""
    
    def __init__(self):
        logger.info("ExecutionHandler initialized")
        # Import inside to avoid circular imports
        from ...shared.instances import reference_manager, prompt_loader
        self.reference_manager = reference_manager
        self.prompt_loader = prompt_loader
    
    async def execute_transformation(
        self,
        prompt: Optional[str] = None,
        ref: Optional[str] = None,
        refs: Optional[List[str]] = None,
        prompt_ref: Optional[str] = None,
        save_as: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute transformation using templates/personas
        
        Priority order for input:
        1. ref - Single reference to transform
        2. refs - Multiple references to combine
        3. prompt_ref - Reference containing the prompt/template
        4. prompt - Direct prompt text
        
        Args:
            prompt: Direct prompt text
            ref: Reference to content to transform
            refs: List of references to combine
            prompt_ref: Reference containing the transformation template
            save_as: Optional reference to save result
            
        Returns:
            Dict with transformation results
        """
        try:
            # Determine input content
            input_content = await self._resolve_input(prompt, ref, refs, prompt_ref)
            
            # Determine transformation template
            template = await self._resolve_template(prompt_ref)
            
            # For now, simulate transformation
            # In real implementation, this would apply the template
            result_content = f"[Transformed using template]\n{input_content}"
            
            # Save if requested
            if save_as:
                await self.reference_manager.create_ref(save_as, result_content)
                logger.info(f"Saved transformation result to {save_as}")
            
            return {
                "status": "executed",
                "input_type": self._determine_input_type(prompt, ref, refs, prompt_ref),
                "template_used": bool(template),
                "saved_as": save_as,
                "content_preview": result_content[:200] + "..." if len(result_content) > 200 else result_content
            }
            
        except Exception as e:
            logger.error(f"Error in execute_transformation: {e}", exc_info=True)
            raise
    
    async def _resolve_input(
        self,
        prompt: Optional[str],
        ref: Optional[str],
        refs: Optional[List[str]],
        prompt_ref: Optional[str]
    ) -> str:
        """Resolve input content based on priority"""
        # Priority: ref > refs > prompt_ref > prompt
        if ref:
            content = await self.reference_manager.read_ref(ref)
            logger.info(f"Using ref '{ref}' as input")
            return content
            
        elif refs:
            contents = []
            for r in refs:
                content = await self.reference_manager.read_ref(r)
                contents.append(content)
            logger.info(f"Combined {len(refs)} references as input")
            return "\n\n---\n\n".join(contents)
            
        elif prompt_ref and not prompt:
            content = await self.reference_manager.read_ref(prompt_ref)
            logger.info(f"Using prompt_ref '{prompt_ref}' as input")
            return content
            
        elif prompt:
            logger.info("Using direct prompt as input")
            return prompt
            
        else:
            raise ValueError("No input provided: specify prompt, ref, refs, or prompt_ref")
    
    async def _resolve_template(self, prompt_ref: Optional[str]) -> Optional[str]:
        """Resolve transformation template if provided"""
        if prompt_ref:
            try:
                template = await self.reference_manager.read_ref(prompt_ref)
                logger.info(f"Loaded template from {prompt_ref}")
                return template
            except Exception as e:
                logger.warning(f"Could not load template from {prompt_ref}: {e}")
                return None
        return None
    
    def _determine_input_type(
        self,
        prompt: Optional[str],
        ref: Optional[str], 
        refs: Optional[List[str]],
        prompt_ref: Optional[str]
    ) -> str:
        """Determine which input type was used"""
        if ref:
            return "single_reference"
        elif refs:
            return "multiple_references"
        elif prompt_ref and not prompt:
            return "prompt_reference"
        elif prompt:
            return "direct_prompt"
        else:
            return "none"
