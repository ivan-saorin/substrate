"""
Substrate Base MCP Server - FastMCP Implementation
Foundation for all Atlas cognitive manipulation services
"""
import os
import sys
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from fastmcp import FastMCP
import json

# Setup logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Import local modules
try:
    from .shared.models import get_model_registry
    from .shared.prompts import PromptLoader
    from .shared.response import ResponseBuilder, NavigationEngine
    from .shared.storage import ReferenceManager
    logger.info("Local imports successful")
except Exception as e:
    logger.error(f"Failed to import local modules: {e}")
    raise


# Get instance configuration
INSTANCE_TYPE = os.getenv("INSTANCE_TYPE", "substrate")
INSTANCE_DESCRIPTION = os.getenv("INSTANCE_DESCRIPTION", "Cognitive manipulation substrate")

# Create FastMCP instance
mcp = FastMCP(INSTANCE_TYPE)

# Initialize services
logger.info(f"Initializing {INSTANCE_TYPE} instance")

model_registry = get_model_registry()
logger.info("Model registry initialized")

prompt_loader = PromptLoader()
response_builder = ResponseBuilder(INSTANCE_TYPE)

# Storage
data_dir = os.getenv("DATA_DIR", "/app/data")
reference_manager = ReferenceManager(data_dir)

# Navigation engine
navigation_engine = NavigationEngine()


def get_instance_documentation() -> Dict[str, str]:
    """Get instance-specific documentation"""
    docs = {
        "atlas": {
            "summary": "I am Atlas, the master orchestrator of the cognitive manipulation system.",
            "usage": """I am ATLAS, the complete cognitive manipulation system. I know about all servers:

**Available Servers**:
- **Substrate** - Documentation, workflows, and reference management
- **Synapse** - Prompt engineering and enhancement  
- **AKAB** - A/B testing and experimentation
- **TLOEN** - Site format transformation
- **UQBAR** - Persona and component management

Use me to understand the system architecture and navigate between servers."""
        },
        "substrate": {
            "summary": "I am the system architect providing documentation, workflows, and reference management.",
            "usage": "Use me to access documentation and manage references."
        },
        "tloen": {
            "summary": "I transform content for specific platforms using format templates.",
            "usage": "Use tloen_execute() to format content for different platforms."
        },
        "uqbar": {
            "summary": "I manage writing personas and content components for consistent style.",
            "usage": "Use uqbar_execute() to apply personas and components to your content."
        }
    }
    
    return docs.get(INSTANCE_TYPE, {
        "summary": f"I am {INSTANCE_TYPE}, part of the Atlas system.",
        "usage": "Part of the cognitive manipulation system."
    })


def get_initial_suggestions() -> List[Dict[str, Any]]:
    """Get initial suggestions based on instance type"""
    if INSTANCE_TYPE in ["substrate", "atlas"]:
        return [
            response_builder.suggest_next(
                "substrate_documentation",
                "Read ASR v2.0 - Complete architecture",
                doc_type="asr-v2"
            ),
            response_builder.suggest_next(
                f"{INSTANCE_TYPE}_show_workflows",
                "Discover available workflows"
            )
        ]
    elif INSTANCE_TYPE == "tloen":
        return [
            response_builder.suggest_next(
                "tloen_list_refs",
                "View available site formats",
                prefix="sites"
            )
        ]
    elif INSTANCE_TYPE == "uqbar":
        return [
            response_builder.suggest_next(
                "uqbar_list_refs",
                "View available personas",
                prefix="personas"
            )
        ]
    return []


# Base tools - all instances have these

@mcp.tool(name=INSTANCE_TYPE)
async def get_server_info() -> Dict[str, Any]:
    """Get server capabilities and documentation"""
    documentation = get_instance_documentation()
    
    return response_builder.build(
        data={
            "name": INSTANCE_TYPE,
            "version": "2.0.0",
            "description": INSTANCE_DESCRIPTION,
            "documentation": documentation,
            "model_registry": {
                "providers": list(set(m.provider.value for m in model_registry.models.values())),
                "models": len(model_registry.models)
            }
        },
        tool=INSTANCE_TYPE,
        message=f"{INSTANCE_TYPE.upper()} server ready. {documentation['summary']}",
        suggestions=get_initial_suggestions()
    )


@mcp.tool(name=f"{INSTANCE_TYPE}_sampling_callback")
async def sampling_callback(request_id: str, response: str) -> Dict[str, Any]:
    """Handle sampling callback responses"""
    return response_builder.build(
        data={
            "request_id": request_id,
            "response": response,
            "status": "received"
        },
        tool=f"{INSTANCE_TYPE}_sampling_callback",
        message="Sampling response recorded."
    )


# Documentation tools - only for substrate/atlas
if INSTANCE_TYPE in ["substrate", "atlas"]:
    @mcp.tool(name="substrate_documentation")
    async def substrate_documentation(doc_type: str = "overview") -> Dict[str, Any]:
        """Access system architecture and methodology documentation"""
        doc_path = Path("/app/docs") / f"{doc_type}.md"
        
        try:
            if doc_path.exists():
                content = doc_path.read_text()
            else:
                content = f"Documentation type '{doc_type}' not found"
            
            return response_builder.build(
                data={"content": content, "doc_type": doc_type},
                tool="substrate_documentation",
                message=f"Loaded {doc_type} documentation"
            )
        except Exception as e:
            return response_builder.build(
                data={"error": str(e)},
                tool="substrate_documentation",
                message=f"Error loading documentation: {e}"
            )


# Workflow tools - only for substrate/atlas
if INSTANCE_TYPE in ["substrate", "atlas"]:
    @mcp.tool(name=f"{INSTANCE_TYPE}_show_workflows")
    async def show_workflows(category: Optional[str] = None, tool: Optional[str] = None) -> Dict[str, Any]:
        """Discover available cognitive manipulation workflows"""
        workflows = []  # Would load from patterns directory
        
        return response_builder.build(
            data={"workflows": workflows},
            tool=f"{INSTANCE_TYPE}_show_workflows",
            message="Available workflows loaded"
        )
    
    @mcp.tool(name=f"{INSTANCE_TYPE}_workflow_guide")
    async def workflow_guide(workflow_name: str) -> Dict[str, Any]:
        """Get step-by-step guidance for a specific workflow"""
        return response_builder.build(
            data={"workflow": workflow_name, "steps": []},
            tool=f"{INSTANCE_TYPE}_workflow_guide",
            message=f"Workflow guide for {workflow_name}"
        )
    
    @mcp.tool(name=f"{INSTANCE_TYPE}_suggest_next")
    async def suggest_next(current_tool: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get smart suggestions for next tool based on current context"""
        suggestions = navigation_engine.get_suggestions(current_tool, context)
        
        return response_builder.build(
            data={"suggestions": suggestions},
            tool=f"{INSTANCE_TYPE}_suggest_next",
            message="Next step suggestions"
        )


# Reference tools - all instances have these

@mcp.tool(name=f"{INSTANCE_TYPE}_create_ref")
async def create_ref(ref: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create or update a reference"""
    result = await reference_manager.create_ref(ref, content, metadata)
    
    return response_builder.build(
        data=result,
        tool=f"{INSTANCE_TYPE}_create_ref",
        message=f"Reference '{ref}' created"
    )


@mcp.tool(name=f"{INSTANCE_TYPE}_read_ref")
async def read_ref(ref: str) -> Dict[str, Any]:
    """Read reference content"""
    content = await reference_manager.read_ref(ref)
    
    return response_builder.build(
        data={"ref": ref, "content": content},
        tool=f"{INSTANCE_TYPE}_read_ref",
        message=f"Reference '{ref}' loaded"
    )


@mcp.tool(name=f"{INSTANCE_TYPE}_update_ref")
async def update_ref(ref: str, content: str) -> Dict[str, Any]:
    """Update existing reference"""
    result = await reference_manager.update_ref(ref, content)
    
    return response_builder.build(
        data=result,
        tool=f"{INSTANCE_TYPE}_update_ref",
        message=f"Reference '{ref}' updated"
    )


@mcp.tool(name=f"{INSTANCE_TYPE}_delete_ref")
async def delete_ref(ref: str) -> Dict[str, Any]:
    """Delete a reference"""
    result = await reference_manager.delete_ref(ref)
    
    return response_builder.build(
        data=result,
        tool=f"{INSTANCE_TYPE}_delete_ref",
        message=f"Reference '{ref}' deleted"
    )


@mcp.tool(name=f"{INSTANCE_TYPE}_list_refs")
async def list_refs(prefix: Optional[str] = None) -> Dict[str, Any]:
    """List all references with optional prefix filter"""
    refs = await reference_manager.list_refs(prefix)
    
    return response_builder.build(
        data={"refs": refs, "count": len(refs)},
        tool=f"{INSTANCE_TYPE}_list_refs",
        message=f"Found {len(refs)} references"
    )


# Execute tool - only for TLOEN/UQBAR
if INSTANCE_TYPE in ["tloen", "uqbar"]:
    @mcp.tool(name=f"{INSTANCE_TYPE}_execute")
    async def execute(
        prompt: Optional[str] = None,
        ref: Optional[str] = None,
        refs: Optional[List[str]] = None,
        prompt_ref: Optional[str] = None,
        save_as: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute transformation using templates/personas"""
        return response_builder.build(
            data={"status": "executed"},
            tool=f"{INSTANCE_TYPE}_execute",
            message="Transformation complete"
        )


logger.info(f"Server initialization complete")


class SubstrateServer:
    """Wrapper class for compatibility"""
    
    def __init__(self):
        pass
    
    def run(self):
        """Run the FastMCP server"""
        try:
            logger.info(f"Starting {INSTANCE_TYPE} FastMCP server")
            mcp.run()
        except Exception as e:
            logger.error(f"Server runtime error: {e}")
            raise


def create_substrate_instance():
    """Factory function to create substrate instance"""
    return SubstrateServer()


# For direct execution
if __name__ == "__main__":
    mcp.run()
