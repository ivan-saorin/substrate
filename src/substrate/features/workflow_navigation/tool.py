"""
Workflow Navigation feature - Tool registration
"""
import logging
from typing import Dict, Any, List, Optional
from .handler import WorkflowHandler

logger = logging.getLogger(__name__)


def register_workflow_tools(mcp) -> List[dict]:
    """
    Register workflow navigation tools with FastMCP
    
    Args:
        mcp: FastMCP instance to register tools on
        
    Returns:
        List of tool metadata
    """
    # Import shared instances
    from ...shared.instances import response_builder, INSTANCE_TYPE
    
    # Only register for substrate/atlas
    if INSTANCE_TYPE not in ["substrate", "atlas"]:
        logger.info(f"Workflow navigation not enabled for {INSTANCE_TYPE}")
        return []
    
    # Create handler instance
    handler = WorkflowHandler()
    
    @mcp.tool(name=f"{INSTANCE_TYPE}_show_workflows")
    async def show_workflows(
        category: Optional[str] = None,
        tool: Optional[str] = None
    ) -> Dict[str, Any]:
        """Discover available cognitive manipulation workflows"""
        try:
            result = await handler.get_workflows(category, tool)
            
            # Build suggestions
            suggestions = []
            
            # If workflows found, suggest exploring one
            if result['workflows']:
                first_workflow = result['workflows'][0]
                suggestions.append(
                    response_builder.suggest_next(
                        f"{INSTANCE_TYPE}_workflow_guide",
                        f"Get step-by-step guide for {first_workflow['name']}",
                        workflow_name=first_workflow['name']
                    )
                )
            
            # Suggest filtering by category
            if not category and result['categories']:
                for cat in result['categories'][:2]:
                    suggestions.append(
                        response_builder.suggest_next(
                            f"{INSTANCE_TYPE}_show_workflows",
                            f"View {cat} workflows",
                            category=cat
                        )
                    )
            
            return response_builder.success(
                data=result,
                message=f"Found {result['count']} workflows",
                suggestions=suggestions
            )
            
        except Exception as e:
            logger.error(f"Error in show_workflows: {e}", exc_info=True)
            return response_builder.error(error=str(e))
    
    @mcp.tool(name=f"{INSTANCE_TYPE}_workflow_guide")
    async def workflow_guide(workflow_name: str) -> Dict[str, Any]:
        """Get step-by-step guidance for a specific workflow"""
        try:
            result = await handler.get_workflow_guide(workflow_name)
            
            # Build suggestions based on first step
            suggestions = []
            if result['steps']:
                first_step = result['steps'][0]
                if first_step.get('tool'):
                    suggestions.append(
                        response_builder.suggest_next(
                            first_step['tool'],
                            f"Start workflow: {first_step.get('description', 'First step')}",
                            **first_step.get('inputs', {})
                        )
                    )
            
            return response_builder.success(
                data=result,
                message=f"Workflow guide for {workflow_name}",
                suggestions=suggestions
            )
            
        except ValueError as e:
            # Workflow not found
            return response_builder.error(
                error=str(e),
                details={
                    "workflow_name": workflow_name,
                    "suggestion": "Use show_workflows to list available workflows"
                }
            )
        except Exception as e:
            logger.error(f"Error in workflow_guide: {e}", exc_info=True)
            return response_builder.error(error=str(e))
    
    @mcp.tool(name=f"{INSTANCE_TYPE}_suggest_next")
    async def suggest_next(
        current_tool: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get smart suggestions for next tool based on current context"""
        try:
            result = await handler.suggest_next_step(current_tool, context)
            
            # No additional suggestions needed - this tool IS the suggester
            return response_builder.success(
                data=result,
                message="Next step suggestions"
            )
            
        except Exception as e:
            logger.error(f"Error in suggest_next: {e}", exc_info=True)
            return response_builder.error(
                error=str(e),
                details={"current_tool": current_tool}
            )
    
    # Return tool metadata
    return [
        {
            "name": f"{INSTANCE_TYPE}_show_workflows",
            "description": "Discover available cognitive manipulation workflows"
        },
        {
            "name": f"{INSTANCE_TYPE}_workflow_guide", 
            "description": "Get step-by-step guidance for a specific workflow"
        },
        {
            "name": f"{INSTANCE_TYPE}_suggest_next",
            "description": "Get smart suggestions for next tool based on current context"
        }
    ]
