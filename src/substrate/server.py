"""Substrate MCP Server - The System Architect."""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import SubstrateMCP

logger = logging.getLogger(__name__)


class SubstrateServer(SubstrateMCP):
    """Substrate documentation and methodology server.
    
    This is the system architect - it knows HOW to build (Atlas) and 
    WHAT to build (System Design) but has no active capabilities.
    """
    
    def __init__(self):
        """Initialize substrate server."""
        # Check for instance type from environment
        instance_type = os.environ.get('INSTANCE_TYPE', 'substrate').lower()
        
        # Configure based on instance type
        if instance_type == 'tloen':
            name = 'tloen'
            description = 'Site format templates and text transformation'
            enable_refs = True
            instructions = (
                "I am TLOEN, the site format specialist. I format content for different platforms "
                "like Reddit, StackOverflow, Twitter, etc. I use templates to transform your content "
                "into platform-specific formats.\n\n"
                "Use tloen_execute() with:\n"
                "- ref: Site format reference (e.g., 'sites/reddit')\n"
                "- prompt: Your content to format\n"
                "- save_as: Optional reference to save result\n\n"
                "The execute method returns a template that LLMs naturally recognize and apply.\n\n"
                "Available formats in refs/sites/:\n"
                "- reddit: Reddit post format\n"
                "- stackoverflow: Q&A format\n"
                "- twitter: Thread format\n"
                "- hackernews: HN submission\n"
                "- medium: Blog post format"
            )
        elif instance_type == 'uqbar':
            name = 'uqbar'
            description = 'Persona management and module composition'
            enable_refs = True
            instructions = (
                "I am UQBAR, the persona and module specialist. I manage writing personas, "
                "voice modules, and component composition for consistent content generation.\n\n"
                "Use uqbar_execute() with:\n"
                "- ref/refs: Persona or module references\n"
                "- prompt: Your content to transform\n"
                "- save_as: Optional reference to save result\n\n"
                "The execute method returns personas/styles that LLMs naturally adopt.\n\n"
                "Available in refs/:\n"
                "- personas/: Writing personas (academic, casual, technical, etc.)\n"
                "- modules/: Reusable components\n"
                "- styles/: Writing style guides"
            )
        else:
            # Default substrate configuration
            name = 'substrate'
            description = 'System architecture and development methodology'
            enable_refs = False
            instructions = (
                "I am the system architect. I tell you HOW to build (Atlas) "
                "and WHAT to build (System Design). I have no active capabilities. "
                "Use me to understand the system architecture and follow the correct "
                "development methodology.\n\n"
                "## Working with Multi-Turn Execution:\n"
                "The substrate architecture supports multi-turn execution through the akab component. "
                "Multi-turn enables fair comparison of LLMs on long-form content generation by allowing "
                "models to continue their responses across multiple interactions until reaching completion.\n\n"
                "### Key Architecture Principles:\n"
                "1. **Hermes Abstraction**: Each MCP server implements its own HermesExecutor for LLM interaction\n"
                "2. **ExecutionRequest/Result**: Standard formats for all LLM executions\n"
                "3. **Blinded Execution**: akab uses BlindedHermes to hide model identities during testing\n\n"
                "### Multi-Turn Flow:\n"
                "1. Initial prompt sent with target length/tokens\n"
                "2. Model generates until hitting token limit\n"
                "3. Continuation prompt sent ('continue' or context reminder)\n"
                "4. Process repeats until natural completion or target reached\n"
                "5. Full response assembled from all turns\n\n"
                "### Implementation Details:\n"
                "- MultiTurnExecutor in akab/multi_turn.py handles continuation logic\n"
                "- Supports both message-based (Anthropic) and prompt-based formats\n"
                "- Tracks metrics: turns used, tokens per turn, total cost\n"
                "- Fair comparison by normalizing for different model token limits\n\n"
                "Refer to Atlas methodology for implementation patterns and System Design "
                "for component responsibilities."
            )
        
        # Store instance type for later use
        self.instance_type = instance_type
        
        super().__init__(
            name=name,
            version="1.0.0",
            description=description,
            instructions=instructions,
            enable_references=enable_refs
        )
        
        # Find docs path relative to this file
        self.docs_path = Path(__file__).parent.parent.parent / "docs"
        
        # Verify docs exist
        if not self.docs_path.exists():
            logger.warning(f"Documentation directory not found: {self.docs_path}")
            # Don't fail, just warn - docs might be in different location
            
        # Register execute tool for TLOEN/UQBAR instances
        if self.instance_type in ['tloen', 'uqbar']:
            self._register_execute_tool()
            
    async def get_capabilities(self) -> Dict[str, Any]:
        """Return substrate capabilities."""
        if self.instance_type == 'tloen':
            return {
                "role": "site_formatter",
                "provides": ["site_formats", "text_transformation", "platform_templates"],
                "actions": ["execute - transform content using site format templates"],
                "formats": ["reddit", "stackoverflow", "twitter", "hackernews", "medium"],
                "example": {
                    "tool": "tloen_execute",
                    "params": {
                        "ref": "sites/reddit",
                        "prompt": "Your content here",
                        "save_as": "output/formatted_post"
                    }
                }
            }
        elif self.instance_type == 'uqbar':
            return {
                "role": "persona_composer",
                "provides": ["personas", "voice_modules", "style_composition"],
                "actions": ["execute - apply personas and style modules to content"],
                "resources": ["personas/*", "modules/*", "styles/*"],
                "example": {
                    "tool": "uqbar_execute",
                    "params": {
                        "ref": "personas/academic",
                        "prompt": "Your content here",
                        "save_as": "output/academic_version"
                    }
                }
            }
        else:
            # Default substrate capabilities
            return {
                "role": "system_architect",
                "provides": ["methodology", "architecture", "component_mapping"],
                "actions": ["none - information only"],
                "documents": ["atlas.md", "system-design.md", "component-map.json"]
            }
    
    def _register_execute_tool(self):
        """Register the execute tool for TLOEN/UQBAR instances."""
        
        @self.tool(name=f"{self.name}_execute")
        async def execute(
            prompt: Optional[str] = None,
            ref: Optional[str] = None,
            refs: Optional[List[str]] = None,
            prompt_ref: Optional[str] = None,
            save_as: Optional[str] = None
        ) -> Dict[str, Any]:
            """Execute transformation using loaded templates/personas.
            
            Priority: ref > refs > prompt_ref > prompt
            
            Returns a template/persona that should be applied to transform content.
            The receiving LLM should recognize the format pattern and generate
            appropriate content following the template structure.
            """
            try:
                # Compose input using standard pattern
                if not self.reference_manager:
                    return self.create_error_response(
                        error="Reference manager not available",
                        suggestions=["Ensure references are enabled for this instance"]
                    )
                    
                input_text = await self._compose_input(prompt, ref, refs, prompt_ref)
                
                # For TLOEN: Apply template formatting
                # For UQBAR: Apply persona/module transformation
                # Return the composed template/persona for LLM pattern matching
                # The LLM will naturally recognize and apply the format
                
                result = input_text
                
                # Save result if requested
                if save_as:
                    await self.reference_manager.create_ref(save_as, result)
                    return self.create_response(
                        success=True,
                        data={"result": result},
                        saved_as=save_as
                    )
                    
                return self.create_response(
                    success=True,
                    data={"result": result}
                )
                
            except Exception as e:
                logger.error(f"Error in execute: {e}")
                return self.create_error_response(
                    error=str(e),
                    error_type="execution_error"
                )


# Don't create server instance at import time
# server = SubstrateServer()
