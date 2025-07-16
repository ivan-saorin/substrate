"""Substrate MCP Server - The System Architect."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from fastmcp import Context

from .base import SubstrateMCP

logger = logging.getLogger(__name__)


class SubstrateServer(SubstrateMCP):
    """Substrate documentation and methodology server.
    
    This is the system architect - it knows HOW to build (Atlas) and 
    WHAT to build (System Design) but has no active capabilities.
    """
    
    def __init__(self):
        """Initialize substrate server."""
        super().__init__(
            name="substrate",
            version="1.0.0",
            description="System architecture and development methodology",
            instructions=(
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
        )
        
        # Find docs path relative to this file
        self.docs_path = Path(__file__).parent.parent.parent / "docs"
        
        # Verify docs exist
        if not self.docs_path.exists():
            raise RuntimeError(f"Documentation directory not found: {self.docs_path}")
            
        # Register substrate-specific tools
        self._register_tools()
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """Return substrate capabilities."""
        return {
            "role": "system_architect",
            "provides": ["methodology", "architecture", "component_mapping"],
            "actions": ["none - information only"],
            "documents": ["atlas.md", "system-design.md", "component-map.json"]
        }
    
    def _register_tools(self):
        """Register substrate-specific tools."""
        
        @self.tool(description="Get system architecture and methodology")
        async def substrate(ctx: Context) -> Dict[str, Any]:
            """Returns complete system documentation.
            
            No parameters - always returns everything you need to know:
            - Atlas (methodology): HOW to build
            - System Design: WHAT to build
            - Component Map: What exists and their responsibilities
            """
            try:
                # Load all documentation
                atlas_path = self.docs_path / "atlas.md"
                design_path = self.docs_path / "system-design.md"
                component_path = self.docs_path / "component-map.json"
                
                # Read documents
                atlas_content = atlas_path.read_text(encoding='utf-8')
                design_content = design_path.read_text(encoding='utf-8')
                
                # Load component map
                with component_path.open('r', encoding='utf-8') as f:
                    component_map = json.load(f)
                
                return self.create_response(
                    success=True,
                    data={
                        "atlas": atlas_content,
                        "system_design": design_content,
                        "component_map": component_map,
                        "instruction": (
                            "Follow these documents EXACTLY. "
                            "Atlas tells you HOW to work. "
                            "System Design tells you WHAT to build. "
                            "Component Map shows what exists. "
                            "Ask if anything is unclear."
                        )
                    }
                )
                
            except FileNotFoundError as e:
                logger.error(f"Documentation file not found: {e}")
                return self.create_response(
                    success=False,
                    error=f"Documentation file not found: {e.filename}",
                    suggestions=[
                        "Ensure substrate is properly installed",
                        "Check that docs/ directory exists",
                        "Verify atlas.md, system-design.md, and component-map.json are present"
                    ]
                )
            except json.JSONDecodeError as e:
                logger.error(f"Invalid component map JSON: {e}")
                return self.create_response(
                    success=False,
                    error="Component map JSON is invalid",
                    suggestions=[
                        "Check component-map.json syntax",
                        "Ensure proper JSON formatting"
                    ]
                )
            except Exception as e:
                logger.error(f"Error loading documentation: {e}")
                return self.create_response(
                    success=False,
                    error=str(e)
                )


# Don't create server instance at import time
# server = SubstrateServer()
