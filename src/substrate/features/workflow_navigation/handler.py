"""
Workflow Navigation feature - Business logic handler
"""
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import yaml

logger = logging.getLogger(__name__)


class WorkflowHandler:
    """Handles workflow discovery and navigation"""
    
    def __init__(self):
        # Get patterns directory
        self.patterns_dir = Path(__file__).parent / "patterns"
        logger.info(f"WorkflowHandler initialized with patterns_dir: {self.patterns_dir}")
        self._workflows_cache = None
    
    async def get_workflows(
        self, 
        category: Optional[str] = None,
        tool: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Discover available cognitive manipulation workflows
        
        Args:
            category: Filter by workflow category
            tool: Filter by workflows containing specific tool
            
        Returns:
            Dict containing filtered workflows
        """
        try:
            # Load all workflows
            workflows = await self._load_all_workflows()
            
            # Apply filters
            filtered = workflows
            
            if category:
                filtered = [w for w in filtered if w.get('category') == category]
                logger.info(f"Filtered to {len(filtered)} workflows in category '{category}'")
            
            if tool:
                filtered = [
                    w for w in filtered 
                    if self._workflow_uses_tool(w, tool)
                ]
                logger.info(f"Filtered to {len(filtered)} workflows using tool '{tool}'")
            
            # Get categories for suggestions
            all_categories = list(set(w.get('category', 'uncategorized') for w in workflows))
            
            return {
                "workflows": filtered,
                "count": len(filtered),
                "categories": all_categories,
                "filters_applied": {
                    "category": category,
                    "tool": tool
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting workflows: {e}", exc_info=True)
            raise
    
    async def get_workflow_guide(self, workflow_name: str) -> Dict[str, Any]:
        """
        Get step-by-step guidance for a specific workflow
        
        Args:
            workflow_name: Name of the workflow
            
        Returns:
            Dict containing workflow details and guidance
        """
        try:
            workflows = await self._load_all_workflows()
            
            # Find workflow by name
            workflow = None
            for w in workflows:
                if w.get('name') == workflow_name:
                    workflow = w
                    break
            
            if not workflow:
                raise ValueError(f"Workflow '{workflow_name}' not found")
            
            # Extract step information
            steps = workflow.get('steps', [])
            step_guide = []
            
            for i, step in enumerate(steps):
                guide_entry = {
                    "step_number": i + 1,
                    "id": step.get('id'),
                    "description": step.get('description'),
                    "tool": step.get('tool'),
                    "inputs": step.get('inputs', {}),
                    "outputs": step.get('outputs', [])
                }
                
                # Add navigation info
                if 'next' in step:
                    if isinstance(step['next'], str):
                        guide_entry['next_step'] = step['next']
                    elif isinstance(step['next'], list):
                        guide_entry['conditional_next'] = step['next']
                
                step_guide.append(guide_entry)
            
            return {
                "workflow": workflow,
                "steps": step_guide,
                "total_steps": len(steps),
                "tags": workflow.get('tags', [])
            }
            
        except Exception as e:
            logger.error(f"Error getting workflow guide: {e}", exc_info=True)
            raise
    
    async def suggest_next_step(
        self,
        current_tool: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get smart suggestions for next tool based on current context
        
        Args:
            current_tool: The tool just executed
            context: Additional context about the execution
            
        Returns:
            Dict containing suggestions
        """
        try:
            # Import navigation engine
            from ...shared.instances import navigation_engine
            
            # Get suggestions from navigation engine
            suggestions = navigation_engine.get_suggestions(
                current_tool,
                context or {}
            )
            
            # Convert to dict format
            suggestion_dicts = []
            for s in suggestions:
                suggestion_dicts.append({
                    "tool": s.tool,
                    "reason": s.reason,
                    "params": s.params,
                    "confidence": s.confidence
                })
            
            return {
                "current_tool": current_tool,
                "suggestions": suggestion_dicts,
                "context_used": bool(context)
            }
            
        except Exception as e:
            logger.error(f"Error getting next suggestions: {e}", exc_info=True)
            raise
    
    async def _load_all_workflows(self) -> List[Dict[str, Any]]:
        """Load all workflow patterns from YAML files"""
        if self._workflows_cache is not None:
            return self._workflows_cache
        
        workflows = []
        
        if not self.patterns_dir.exists():
            logger.warning(f"Patterns directory not found: {self.patterns_dir}")
            return workflows
        
        # Load each YAML file
        for yaml_file in self.patterns_dir.glob("*.yaml"):
            if yaml_file.name == "index.yaml":
                continue  # Skip index file
                
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    workflow = yaml.safe_load(f)
                    
                if workflow and isinstance(workflow, dict):
                    # Add source file info
                    workflow['source_file'] = yaml_file.name
                    workflows.append(workflow)
                    logger.debug(f"Loaded workflow from {yaml_file.name}")
                    
            except Exception as e:
                logger.error(f"Error loading workflow from {yaml_file}: {e}")
        
        self._workflows_cache = workflows
        logger.info(f"Loaded {len(workflows)} workflows")
        return workflows
    
    def _workflow_uses_tool(self, workflow: Dict[str, Any], tool: str) -> bool:
        """Check if a workflow uses a specific tool"""
        steps = workflow.get('steps', [])
        
        for step in steps:
            step_tool = step.get('tool', '')
            if tool in step_tool:
                return True
        
        return False
