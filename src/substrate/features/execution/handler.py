"""
Execution feature - Business logic handler
"""
import os
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class ExecutionHandler:
    """Handles pattern execution for TLOEN/UQBAR instances"""
    
    def __init__(self):
        logger.info("ExecutionHandler initialized")
        # Import inside to avoid circular imports
        from ...shared.instances import reference_manager, prompt_loader
        from ...shared.api.clear_hermes import ClearHermes
        from ...shared.models import get_model_registry
        self.reference_manager = reference_manager
        self.prompt_loader = prompt_loader
        self.hermes = ClearHermes()
        self.model_registry = get_model_registry()
    
    async def execute_transformation(
        self,
        prompt: Optional[str] = None,
        ref: Optional[str] = None,
        refs: List[str] = [],
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
            
            # Apply transformation using LLM
            result_content = await self._apply_transformation(input_content, ref, refs, template)
            
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
        refs: List[str],
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
        refs: List[str],
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
    
    async def _apply_transformation(
        self,
        input_content: str,
        ref: Optional[str],
        refs: List[str],
        template: Optional[str]
    ) -> str:
        """Apply transformation using LLM"""
        try:
            # Get instance type to determine transformation type
            instance_type = os.getenv('INSTANCE_TYPE', 'substrate').lower()
            
            # Build execution prompt - simple unified approach
            if ref:
                # Load the template/persona as a "program"
                program = await self.reference_manager.read_ref(ref)
                
                # Replace placeholders in the program
                program = program.replace('{{content}}', input_content)
                program = program.replace('{{topic}}', input_content)  # For compatibility
                
                # Execute as a program
                execution_prompt = f"execute the following program:\n{program}"
            elif template:
                # Use provided template
                execution_prompt = f"execute the following program:\n{template.replace('{content}', input_content)}"
            else:
                # Direct execution
                execution_prompt = input_content
            
            # Get model (default to anthropic_m)
            model = self.model_registry.get('anthropic_m')
            if not model:
                logger.error("No model available for transformation")
                return input_content
            
            logger.info(f"Using model: {model.api_name} ({model.identifier})")
            
            # Call LLM
            result = await self.hermes.complete(
                model=model,
                prompt=execution_prompt,
                max_tokens=2000,
                temperature=0.7
            )
            
            return result['content']
            
        except Exception as e:
            logger.error(f"Error applying transformation: {e}", exc_info=True)
            # Fallback to original content
            return input_content

