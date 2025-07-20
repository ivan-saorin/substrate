"""Workflow navigation feature - Discover and guide through cognitive manipulation workflows"""
from typing import Dict, Any, List, Optional
import os
from pathlib import Path
import fastmcp.types as types


def register_workflow_tools(server) -> List[dict]:
    """Register workflow navigation tools on the server"""
    
    async def show_workflows(
        category: Optional[str] = None,
        tool: Optional[str] = None
    ) -> Dict[str, Any]:
        """Show available workflows
        
        Args:
            category: Filter by category (e.g., 'prompt_optimization', 'content_pipeline')
            tool: Show workflows that include specific tool
        """
        workflows = _load_workflows(server)
        
        # Filter if requested
        if category:
            workflows = [w for w in workflows if w.get('category') == category]
        
        if tool:
            workflows = [w for w in workflows if _workflow_includes_tool(w, tool)]
        
        # Format workflows for display
        formatted = []
        for workflow in workflows:
            formatted.append({
                "name": workflow['name'],
                "description": workflow.get('description', ''),
                "category": workflow.get('category', 'general'),
                "steps": len(workflow.get('steps', [])),
                "tools": _extract_tools_from_workflow(workflow),
                "tags": workflow.get('tags', [])
            })
        
        suggestions = []
        if formatted:
            # Suggest trying the first workflow
            first = formatted[0]
            if first['tools']:
                suggestions.append(
                    server.response_builder.suggest_next(
                        first['tools'][0],
                        f"Start '{first['name']}' workflow"
                    )
                )
        
        return server.response_builder.success(
            data={
                "workflows": formatted,
                "count": len(formatted),
                "filters": {
                    "category": category,
                    "tool": tool
                }
            },
            message=f"Found {len(formatted)} workflows",
            suggestions=suggestions
        )
    
    async def workflow_guide(workflow_name: str) -> Dict[str, Any]:
        """Get detailed workflow guidance
        
        Args:
            workflow_name: Name of the workflow to guide through
        """
        workflows = _load_workflows(server)
        
        # Find workflow
        workflow = None
        for w in workflows:
            if w['name'].lower() == workflow_name.lower():
                workflow = w
                break
        
        if not workflow:
            return server.response_builder.error(
                f"Workflow not found: {workflow_name}",
                details={"available": [w['name'] for w in workflows]}
            )
        
        # Format steps with details
        steps = []
        for i, step in enumerate(workflow.get('steps', [])):
            steps.append({
                "step": i + 1,
                "id": step.get('id', f'step_{i+1}'),
                "tool": step.get('tool', ''),
                "description": step.get('description', ''),
                "inputs": step.get('inputs', {}),
                "outputs": step.get('outputs', []),
                "next": step.get('next', [])
            })
        
        # Suggest starting the workflow
        suggestions = []
        if steps:
            first_tool = steps[0]['tool']
            if first_tool:  # Only suggest if tool is specified
                suggestions.append(
                    server.response_builder.suggest_next(
                        first_tool,
                        f"Start workflow: {workflow_name}"
                    )
                )
        
        return server.response_builder.success(
            data={
                "workflow": workflow_name,
                "description": workflow.get('description', ''),
                "category": workflow.get('category', 'general'),
                "tags": workflow.get('tags', []),
                "version": workflow.get('version', '1.0'),
                "steps": steps,
                "total_steps": len(steps)
            },
            message=f"Workflow guide: {workflow_name}",
            suggestions=suggestions
        )
    
    async def suggest_next(
        current_tool: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get next tool suggestions
        
        Args:
            current_tool: The tool just used
            context: Optional context (output refs, etc.)
        """
        suggestions = server.navigation_engine.get_suggestions(current_tool, context or {})
        
        # Convert to simple format
        formatted = []
        for suggestion in suggestions:
            formatted.append({
                "tool": suggestion.tool,
                "reason": suggestion.reason,
                "params": suggestion.params,
                "confidence": suggestion.confidence
            })
        
        # Also check workflows for additional suggestions
        workflow_suggestions = _get_workflow_based_suggestions(server, current_tool, context)
        formatted.extend(workflow_suggestions)
        
        # Sort by confidence and deduplicate
        seen = set()
        unique_suggestions = []
        for s in sorted(formatted, key=lambda x: x.get('confidence', 0), reverse=True):
            tool_key = s['tool']
            if tool_key not in seen:
                seen.add(tool_key)
                unique_suggestions.append(s)
        
        return server.response_builder.success(
            data={
                "current_tool": current_tool,
                "suggestions": unique_suggestions[:5],  # Top 5
                "context": context
            },
            message=f"Found {len(unique_suggestions)} suggestions for next steps"
        )
    
    # Register tools
    server.register_tool(f"{server.instance_type}_show_workflows", show_workflows)
    server.register_tool(f"{server.instance_type}_workflow_guide", workflow_guide)  
    server.register_tool(f"{server.instance_type}_suggest_next", suggest_next)
    
    # Return tool metadata
    tools = [
        {
            "name": f"{server.instance_type}_show_workflows",
            "description": "Discover available cognitive manipulation workflows"
        },
        {
            "name": f"{server.instance_type}_workflow_guide",
            "description": "Get step-by-step guidance for a specific workflow"
        },
        {
            "name": f"{server.instance_type}_suggest_next",
            "description": "Get smart suggestions for next tool based on current context"
        }
    ]
    
    return tools


def _load_workflows(server) -> List[Dict[str, Any]]:
    """Load workflow definitions from YAML files"""
    workflows = []
    
    # Get patterns directory
    patterns_dir = Path(__file__).parent / "patterns"
    
    if patterns_dir.exists():
        # Load all YAML files
        for yaml_file in patterns_dir.glob("*.yaml"):
            try:
                workflow = server.prompt_loader.load_yaml(str(yaml_file))
                workflows.append(workflow)
            except Exception as e:
                # Log error but continue loading other workflows
                import logging
                logging.error(f"Failed to load workflow {yaml_file}: {e}")
    
    return workflows


def _workflow_includes_tool(workflow: Dict[str, Any], tool: str) -> bool:
    """Check if workflow includes a specific tool"""
    for step in workflow.get('steps', []):
        if step.get('tool') == tool:
            return True
    return False


def _extract_tools_from_workflow(workflow: Dict[str, Any]) -> List[str]:
    """Extract all tools used in a workflow"""
    tools = []
    for step in workflow.get('steps', []):
        tool = step.get('tool')
        if tool:  # Only add if tool is specified
            tools.append(tool)
    return tools


def _get_workflow_based_suggestions(server, current_tool: str, 
                                   context: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Get suggestions based on workflow patterns"""
    suggestions = []
    workflows = _load_workflows(server)
    
    for workflow in workflows:
        steps = workflow.get('steps', [])
        
        # Find current tool in workflow
        for i, step in enumerate(steps):
            if step.get('tool') == current_tool:
                # Look at next steps
                next_steps = step.get('next', [])
                
                if isinstance(next_steps, list):
                    # Handle conditional next steps
                    for next_step in next_steps:
                        if isinstance(next_step, dict):
                            goto = next_step.get('goto')
                            condition = next_step.get('condition', 'default')
                            
                            # Find the target step
                            target_step = None
                            for s in steps:
                                if s.get('id') == goto:
                                    target_step = s
                                    break
                            
                            if target_step and target_step.get('tool'):
                                suggestions.append({
                                    "tool": target_step['tool'],
                                    "reason": f"Continue '{workflow['name']}' workflow ({condition})",
                                    "params": _build_workflow_params(step, target_step, context),
                                    "confidence": 0.7
                                })
                elif isinstance(next_steps, str):
                    # Simple next step
                    target_step = None
                    for s in steps:
                        if s.get('id') == next_steps:
                            target_step = s
                            break
                    
                    if target_step and target_step.get('tool'):
                        suggestions.append({
                            "tool": target_step['tool'],
                            "reason": f"Continue '{workflow['name']}' workflow",
                            "params": _build_workflow_params(step, target_step, context),
                            "confidence": 0.8
                        })
                elif i < len(steps) - 1:
                    # No explicit next, use sequential
                    next_step = steps[i + 1]
                    if next_step.get('tool'):
                        suggestions.append({
                            "tool": next_step['tool'],
                            "reason": f"Next step in '{workflow['name']}' workflow",
                            "params": _build_workflow_params(step, next_step, context),
                            "confidence": 0.6
                        })
    
    return suggestions


def _build_workflow_params(current_step: Dict[str, Any], 
                          next_step: Dict[str, Any], 
                          context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Build parameters for next step based on workflow definition"""
    params = {}
    
    if not context:
        return params
    
    # Extract outputs from current step that might be inputs to next
    current_outputs = {out['name']: out for out in current_step.get('outputs', [])}
    next_inputs = next_step.get('inputs', {})
    
    # Map outputs to inputs
    for input_name, input_spec in next_inputs.items():
        if isinstance(input_spec, str) and input_spec.startswith('$outputs.'):
            # Reference to previous output
            output_ref = input_spec.replace('$outputs.', '').split('.')[-1]
            if output_ref in current_outputs:
                # Map from context if available
                if 'output_ref' in context:
                    params[input_name] = context['output_ref']
                elif 'saved_as' in context:
                    params[input_name] = context['saved_as']
        elif input_spec == 'required' and input_name in context:
            # Direct mapping from context
            params[input_name] = context[input_name]
    
    return params


def get_tool_schemas(instance_type: str) -> List[types.Tool]:
    """Get FastMCP tool schemas for workflow tools"""
    # Only substrate and atlas get workflow tools
    if instance_type not in ["substrate", "atlas"]:
        return []
    
    return [
        types.Tool(
            name=f"{instance_type}_show_workflows",
            description="Discover available cognitive manipulation workflows",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {"type": "string"},
                    "tool": {"type": "string"}
                },
                "required": []
            }
        ),
        types.Tool(
            name=f"{instance_type}_workflow_guide",
            description="Get step-by-step guidance for a specific workflow",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_name": {"type": "string"}
                },
                "required": ["workflow_name"]
            }
        ),
        types.Tool(
            name=f"{instance_type}_suggest_next",
            description="Get smart suggestions for next tool based on current context",
            inputSchema={
                "type": "object",
                "properties": {
                    "current_tool": {"type": "string"},
                    "context": {"type": "object"}
                },
                "required": ["current_tool"]
            }
        )
    ]
