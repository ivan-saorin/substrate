"""
Response Builder - Standardized responses with navigation hints
"""
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class NavigationSuggestion:
    """Suggestion for next tool to use"""
    tool: str
    reason: str
    params: Dict[str, Any]
    confidence: float = 0.8
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return {
            'tool': self.tool,
            'reason': self.reason,
            'params': self.params
        }


class ResponseBuilder:
    """Builder for standardized MCP responses"""
    
    def __init__(self, server_name: str):
        self.server_name = server_name
    
    def build(self, 
              data: Any,
              tool: Optional[str] = None,
              suggestions: Optional[List[NavigationSuggestion]] = None,
              message: Optional[str] = None,
              metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Build standardized response
        
        Args:
            data: The actual response data
            tool: Tool name that generated this response
            suggestions: Navigation suggestions for next steps
            message: Human-readable message
            metadata: Additional metadata
            
        Returns:
            Standardized response dictionary
        """
        response = {
            'data': data,
            'metadata': {
                'server': self.server_name,
                'timestamp': time.time()
            }
        }
        
        if tool:
            response['metadata']['tool'] = tool
            
        if metadata:
            response['metadata'].update(metadata)
        
        if suggestions:
            # Convert suggestions to dict format
            response['suggestions'] = [
                s.to_dict() if isinstance(s, NavigationSuggestion) else s
                for s in suggestions
            ]
        
        if message:
            response['message'] = message
            
        return response
    
    def error(self, error: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Build error response"""
        return self.build(
            data={'error': error, 'details': details or {}},
            metadata={'status': 'error'}
        )
    
    def success(self, data: Any, message: Optional[str] = None,
                suggestions: Optional[List[NavigationSuggestion]] = None) -> Dict[str, Any]:
        """Build success response with optional navigation"""
        return self.build(
            data=data,
            message=message,
            suggestions=suggestions,
            metadata={'status': 'success'}
        )
    
    @staticmethod
    def suggest_next(tool: str, reason: str, **params) -> NavigationSuggestion:
        """Helper to create navigation suggestion"""
        return NavigationSuggestion(
            tool=tool,
            reason=reason,
            params=params
        )


class NavigationEngine:
    """Engine for generating smart navigation suggestions"""
    
    def __init__(self):
        # Tool relationships mapping
        self.tool_graph = {
            # Synapse tools
            'synapse:enhance_prompt': [
                ('akab:create_campaign', 'Test enhanced vs original prompt performance'),
                ('akab:quick_compare', 'Quick comparison across providers'),
                ('synapse:analyze_pattern_effectiveness', 'Analyze which patterns worked best'),
                ('tloen:platform_format', 'Format for specific platform')
            ],
            
            'synapse:stable_genius': [
                ('substrate:create_ref', 'Save generated content'),
                ('synapse:enhance_prompt', 'Further enhance the generated prompt'),
                ('akab:create_campaign', 'Test variations of the genius prompt')
            ],
            
            'synapse:analyze_pattern_effectiveness': [
                ('synapse:enhance_prompt', 'Apply recommended patterns'),
                ('synapse:list_available_patterns', 'Explore other pattern options')
            ],
            
            # AKAB tools
            'akab:quick_compare': [
                ('akab:create_campaign', 'Create full A/B test campaign'),
                ('synapse:enhance_prompt', 'Enhance the best performing version')
            ],
            
            'akab:create_campaign': [
                ('akab:execute_campaign', 'Run the campaign'),
                ('akab:list_campaigns', 'View all campaigns')
            ],
            
            'akab:execute_campaign': [
                ('akab:analyze_results', 'Analyze campaign results'),
                ('akab:cost_report', 'View cost breakdown')
            ],
            
            'akab:analyze_results': [
                ('akab:unlock', 'Reveal model mappings'),
                ('synapse:enhance_prompt', 'Enhance based on winning variant'),
                ('akab:create_campaign', 'Create follow-up campaign')
            ],
            
            # Substrate tools
            'substrate:create_ref': [
                ('substrate:read_ref', 'Read saved reference'),
                ('substrate:list_refs', 'View all references'),
                ('synapse:enhance_prompt', 'Enhance saved content')
            ],
            
            'substrate:read_ref': [
                ('substrate:update_ref', 'Update reference content'),
                ('substrate:execute', 'Execute as pattern'),
                ('synapse:enhance_prompt', 'Enhance content')
            ],
            
            # TLOEN tools
            'tloen:platform_format': [
                ('substrate:create_ref', 'Save formatted version'),
                ('akab:quick_compare', 'Compare platform effectiveness')
            ],
            
            # UQBAR tools  
            'uqbar:library_access': [
                ('substrate:create_ref', 'Save selected template'),
                ('substrate:execute', 'Apply template'),
                ('tloen:platform_format', 'Format for platform')
            ]
        }
        
        # Workflow patterns
        self.workflow_patterns = {
            'prompt_optimization': [
                'synapse:analyze_pattern_effectiveness',
                'synapse:enhance_prompt',
                'akab:create_campaign',
                'akab:execute_campaign',
                'akab:analyze_results'
            ],
            
            'content_pipeline': [
                'synapse:stable_genius',
                'substrate:create_ref',
                'tloen:platform_format',
                'substrate:create_ref'
            ],
            
            'quick_testing': [
                'akab:quick_compare',
                'synapse:enhance_prompt',
                'akab:quick_compare'
            ]
        }
    
    def get_suggestions(self, current_tool: str, context: Dict[str, Any]) -> List[NavigationSuggestion]:
        """Get navigation suggestions based on current tool and context"""
        suggestions = []
        
        # Get direct tool relationships
        if current_tool in self.tool_graph:
            for next_tool, reason in self.tool_graph[current_tool]:
                # Build params based on context
                params = self._build_params(current_tool, next_tool, context)
                
                suggestions.append(NavigationSuggestion(
                    tool=next_tool,
                    reason=reason,
                    params=params,
                    confidence=0.9
                ))
        
        # Add workflow-based suggestions
        workflow_suggestions = self._get_workflow_suggestions(current_tool, context)
        suggestions.extend(workflow_suggestions)
        
        # Sort by confidence and limit
        suggestions.sort(key=lambda s: s.confidence, reverse=True)
        return suggestions[:5]  # Top 5 suggestions
    
    def _build_params(self, from_tool: str, to_tool: str, 
                      context: Dict[str, Any]) -> Dict[str, Any]:
        """Build parameters for next tool based on context"""
        params = {}
        
        # Extract output reference if available
        if 'output_ref' in context:
            if 'ref' in to_tool or 'prompt' in to_tool:
                params['prompt_ref'] = context['output_ref']
        
        # Map specific tool transitions
        if from_tool == 'synapse:enhance_prompt' and to_tool == 'akab:create_campaign':
            params['base_prompt'] = '$ref'
            params['models'] = context.get('models', [])
            
        elif from_tool == 'akab:create_campaign' and to_tool == 'akab:execute_campaign':
            params['campaign_id'] = context.get('campaign_id', '$last_campaign')
            
        elif from_tool == 'akab:execute_campaign' and to_tool == 'akab:analyze_results':
            params['campaign_id'] = context.get('campaign_id', '$last_campaign')
        
        return params
    
    def _get_workflow_suggestions(self, current_tool: str, 
                                 context: Dict[str, Any]) -> List[NavigationSuggestion]:
        """Get suggestions based on workflow patterns"""
        suggestions = []
        
        for workflow_name, tools in self.workflow_patterns.items():
            if current_tool in tools:
                idx = tools.index(current_tool)
                if idx < len(tools) - 1:
                    next_tool = tools[idx + 1]
                    suggestions.append(NavigationSuggestion(
                        tool=next_tool,
                        reason=f"Continue {workflow_name} workflow",
                        params={},
                        confidence=0.7
                    ))
        
        return suggestions
