"""
Execution feature - Tool registration for TLOEN/UQBAR
"""
import logging
from typing import Dict, Any, List, Optional
from .handler import ExecutionHandler

logger = logging.getLogger(__name__)


def register_execution_tools(mcp) -> List[dict]:
    """
    Register execution tool for TLOEN/UQBAR instances
    
    Args:
        mcp: FastMCP instance to register tools on
        
    Returns:
        List of tool metadata
    """
    # Import shared instances
    from ...shared.instances import response_builder, INSTANCE_TYPE
    
    # Only register for TLOEN/UQBAR
    if INSTANCE_TYPE not in ["tloen", "uqbar"]:
        logger.info(f"Execution feature not enabled for {INSTANCE_TYPE}")
        return []
    
    # Create handler instance
    handler = ExecutionHandler()
    
    @mcp.tool(name=f"{INSTANCE_TYPE}_execute")
    async def execute(
        prompt: Optional[str] = None,
        ref: Optional[str] = None,
        refs: List[str] = [],
        prompt_ref: Optional[str] = None,
        save_as: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute transformation using templates/personas"""
        try:
            result = await handler.execute_transformation(
                prompt=prompt,
                ref=ref,
                refs=refs,
                prompt_ref=prompt_ref,
                save_as=save_as
            )
            
            # Build suggestions based on result
            suggestions = []
            
            if save_as:
                suggestions.append(
                    response_builder.suggest_next(
                        f"{INSTANCE_TYPE}_read_ref",
                        "Read the transformation result",
                        ref=save_as
                    )
                )
            
            # Suggest format conversion if TLOEN
            if INSTANCE_TYPE == "tloen" and save_as:
                suggestions.append(
                    response_builder.suggest_next(
                        f"{INSTANCE_TYPE}_execute",
                        "Apply another format",
                        ref=save_as,
                        prompt_ref="sites/twitter"  # Example
                    )
                )
            
            # Suggest persona application if UQBAR
            if INSTANCE_TYPE == "uqbar" and save_as:
                suggestions.append(
                    response_builder.suggest_next(
                        f"{INSTANCE_TYPE}_execute",
                        "Apply another persona",
                        ref=save_as,
                        prompt_ref="personas/shakespeare"  # Example
                    )
                )
            
            return response_builder.success(
                data=result,
                message="Transformation complete",
                suggestions=suggestions
            )
            
        except ValueError as e:
            # Handle missing input gracefully
            return response_builder.error(
                error=str(e),
                details={
                    "hint": "Provide at least one of: prompt, ref, refs, or prompt_ref"
                }
            )
        except Exception as e:
            logger.error(f"Error in execute: {e}", exc_info=True)
            return response_builder.error(
                error=str(e),
                details={
                    "input_type": handler._determine_input_type(prompt, ref, refs, prompt_ref)
                }
            )
    
    # Return tool metadata
    return [{
        "name": f"{INSTANCE_TYPE}_execute",
        "description": "Execute transformation using templates/personas"
    }]
