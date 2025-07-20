"""Execution feature - Execute patterns for TLOEN/UQBAR instances"""
from typing import Dict, Any, List, Optional


def register_execution_tools(server) -> List[dict]:
    """Register execution tools on the server"""
    tools = []
    
    # Only register for TLOEN/UQBAR instances
    if server.instance_type not in ['tloen', 'uqbar']:
        return tools
    
    async def execute(
        prompt: Optional[str] = None,
        ref: Optional[str] = None,
        refs: Optional[List[str]] = None,
        prompt_ref: Optional[str] = None,
        save_as: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute transformation using loaded templates/personas
        
        Priority: ref > refs > prompt_ref > prompt
        
        Returns a template/persona that should be applied to transform content.
        The receiving LLM should recognize the format pattern and generate
        appropriate content following the template structure.
        
        Args:
            prompt: Direct prompt text
            ref: Reference to template/persona
            refs: Multiple references to combine
            prompt_ref: Reference containing prompt
            save_as: Optional reference to save result
        """
        try:
            # Compose input using priority
            input_text = await _compose_input(server, prompt, ref, refs, prompt_ref)
            
            if not input_text:
                return server.response_builder.error(
                    "No input provided",
                    details={
                        "hint": "Provide prompt, ref, refs, or prompt_ref",
                        "priority": "ref > refs > prompt_ref > prompt"
                    }
                )
            
            # For TLOEN: This would be a site format template
            # For UQBAR: This would be a persona/style guide
            # The LLM will naturally recognize and apply the pattern
            
            result = input_text
            
            # Build suggestions based on instance type
            suggestions = []
            
            if server.instance_type == 'tloen':
                suggestions = [
                    server.response_builder.suggest_next(
                        "substrate:create_ref",
                        "Save formatted result",
                        content=result
                    ),
                    server.response_builder.suggest_next(
                        "akab:quick_compare",
                        "Compare platform effectiveness",
                        prompt=result
                    )
                ]
            elif server.instance_type == 'uqbar':
                suggestions = [
                    server.response_builder.suggest_next(
                        "substrate:create_ref",
                        "Save styled content",
                        content=result
                    ),
                    server.response_builder.suggest_next(
                        "tloen:execute",
                        "Format for specific platform",
                        prompt=result
                    )
                ]
            
            # Save if requested
            if save_as:
                await server.reference_manager.create_ref(save_as, result)
                
                return server.response_builder.success(
                    data={
                        "result": result,
                        "saved_as": save_as
                    },
                    message=f"Transformation complete and saved to {save_as}",
                    suggestions=suggestions
                )
            
            return server.response_builder.success(
                data={"result": result},
                message="Transformation complete",
                suggestions=suggestions
            )
            
        except Exception as e:
            return server.response_builder.error(
                f"Execution error: {str(e)}",
                details={"error_type": "execution_error"}
            )
    
    # Register the tool
    server.register_tool(f"{server.instance_type}_execute", execute)
    
    tools.append({
        "name": f"{server.instance_type}_execute",
        "description": f"Execute transformation using {server.instance_type} templates/personas"
    })
    
    return tools


async def _compose_input(server, prompt: Optional[str] = None,
                        ref: Optional[str] = None,
                        refs: Optional[List[str]] = None,
                        prompt_ref: Optional[str] = None) -> str:
    """Compose input from various sources using priority order"""
    
    # Priority: ref > refs > prompt_ref > prompt
    if ref:
        # Load single reference
        content = await server.reference_manager.read_ref(ref)
        return content
    
    elif refs:
        # Combine multiple references
        contents = []
        for r in refs:
            try:
                content = await server.reference_manager.read_ref(r)
                contents.append(f"=== {r} ===\n{content}")
            except FileNotFoundError:
                contents.append(f"=== {r} ===\n[Reference not found]")
        
        return "\n\n".join(contents)
    
    elif prompt_ref:
        # Load prompt from reference
        content = await server.reference_manager.read_ref(prompt_ref)
        return content
    
    elif prompt:
        # Direct prompt
        return prompt
    
    return ""
