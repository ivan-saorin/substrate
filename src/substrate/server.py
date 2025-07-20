"""
Substrate Base MCP Server
Foundation for all Atlas cognitive manipulation services
"""
import os
import sys
import logging
from typing import Dict, Any, Optional, List
from fastmcp import FastMCP
import fastmcp.types as types

# Setup logging
logger = logging.getLogger(__name__)

try:
    from .shared.models import get_model_registry
    from .shared.prompts import PromptLoader
    from .shared.response import ResponseBuilder, NavigationEngine
    from .shared.storage import ReferenceManager
    from .features import (
        register_documentation_tools,
        register_reference_tools,
        register_execution_tools,
        register_workflow_tools
    )
    logger.info("Local imports successful")
except Exception as e:
    logger.error(f"Failed to import local modules: {e}")
    raise


class SubstrateServer:
    """Base MCP server for cognitive manipulation substrate"""
    
    def __init__(self):
        self.name = "substrate"
        self.server = FastMCP(self.name)
        self.instance_type = os.getenv("INSTANCE_TYPE", "substrate")
        self.instance_description = os.getenv("INSTANCE_DESCRIPTION", "Cognitive manipulation substrate")
        
        logger.info(f"Initializing {self.instance_type} instance")
        
        # Core services
        self.model_registry = get_model_registry()
        logger.info("Model registry initialized")
        
        self.prompt_loader = PromptLoader()
        self.response_builder = ResponseBuilder(self.instance_type)
        
        # Storage
        self.data_dir = os.getenv("DATA_DIR", "/app/data")
        self.reference_manager = ReferenceManager(self.data_dir)
        
        # Navigation engine for suggestions
        self.navigation_engine = NavigationEngine()
        
        # Current tool tracking for response builder
        self._current_tool = None
        
        # Tool handlers storage
        self._tool_handlers = {}
        
        # Register handlers
        self._register_handlers()
        logger.info("Handlers registered successfully")
        
        # Register tools
        self._register_tools()
        logger.info(f"Registered {len(self._tool_handlers)} tool handlers")
        
        logger.info(f"Server initialization complete with {len(self._tool_handlers)} tools")
        
    def _register_handlers(self):
        """Register server handlers"""
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List available tools"""
            return self._get_tools_for_instance()
            
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """Handle tool calls"""
            logger.debug(f"Tool called: {name} with args: {arguments}")
            
            # Set current tool for response builder
            self._current_tool = name
            
            try:
                # Get the tool handler
                if name in self._tool_handlers:
                    result = await self._tool_handlers[name](**arguments)
                else:
                    result = {"error": f"Unknown tool: {name}"}
                
                # Convert result to JSON string
                import json
                result_str = json.dumps(result, indent=2)
                
                return [types.TextContent(
                    type="text",
                    text=result_str
                )]
                
            except Exception as e:
                logger.error(f"Error in tool {name}: {e}")
                error_result = {
                    "error": str(e),
                    "tool": name,
                    "type": "execution_error"
                }
                return [types.TextContent(
                    type="text", 
                    text=json.dumps(error_result, indent=2)
                )]
            finally:
                self._current_tool = None
    
    def _register_tools(self):
        """Register all tools"""
        # Register base tools
        self._register_base_tools()
        
        # Register feature-based tools
        if self.instance_type in ["substrate", "atlas"]:
            # Full substrate and atlas get everything
            register_documentation_tools(self)
            register_reference_tools(self)
            register_execution_tools(self)
            register_workflow_tools(self)
        elif self.instance_type == "tloen":
            # TLOEN is transformation focused
            register_reference_tools(self)
            register_execution_tools(self)
        elif self.instance_type == "uqbar":
            # UQBAR is library/catalog focused
            register_reference_tools(self)
            register_execution_tools(self)
            
        # Log registered tools
        for tool_name in self._tool_handlers:
            logger.info(f"Registered tool: {tool_name}")
    
    def _register_base_tools(self):
        """Register base tools that all servers have"""
        # Server info tool - this is the self-documenting tool
        async def get_server_info() -> Dict[str, Any]:
            """Get server capabilities and info"""
            
            # Get instance-specific documentation
            documentation = self._get_instance_documentation()
            
            # Get available tools for this instance
            tools_list = []
            for tool_name, handler in self._tool_handlers.items():
                if tool_name != self.instance_type:  # Don't include self
                    tools_list.append({
                        "name": tool_name,
                        "description": handler.__doc__ or "No description"
                    })
            
            # Build suggestions based on instance type
            suggestions = []
            
            if self.instance_type in ["substrate", "atlas"]:
                # Both substrate and atlas get full documentation access
                suggestions = [
                    self.response_builder.suggest_next(
                        "substrate_documentation",
                        "Read ASR v2.0 - Complete architecture",
                        doc_type="asr-v2"
                    ),
                    self.response_builder.suggest_next(
                        "substrate_documentation",
                        "Read Atlas methodology",
                        doc_type="atlas"
                    ),
                    self.response_builder.suggest_next(
                        f"{self.instance_type}:show_workflows",
                        "Discover available workflows"
                    )
                ]
            elif self.instance_type == "tloen":
                suggestions = [
                    self.response_builder.suggest_next(
                        "tloen:list_refs",
                        "View available site formats",
                        prefix="sites"
                    ),
                    self.response_builder.suggest_next(
                        "tloen:execute",
                        "Format content for a platform"
                    )
                ]
            elif self.instance_type == "uqbar":
                suggestions = [
                    self.response_builder.suggest_next(
                        "uqbar:list_refs",
                        "View available personas",
                        prefix="personas"
                    ),
                    self.response_builder.suggest_next(
                        "uqbar:list_refs",
                        "View available components",
                        prefix="components"
                    )
                ]
            
            return self.response_builder.build(
                data={
                    "name": self.instance_type,
                    "version": "2.0.0",
                    "description": self.instance_description,
                    "documentation": documentation,
                    "tools": tools_list,
                    "tool_count": len(self._tool_handlers),
                    "model_registry": {
                        "providers": list(set(m.provider.value for m in self.model_registry.models.values())),
                        "models": len(self.model_registry.models)
                    }
                },
                tool=self.instance_type,
                message=f"{self.instance_type.upper()} server ready. {documentation['summary']}",
                suggestions=suggestions
            )
        
        self._tool_handlers[self.instance_type] = get_server_info
        
        # Sampling callback
        async def sampling_callback(request_id: str, response: str) -> Dict[str, Any]:
            """Handle sampling responses"""
            return self.response_builder.build(
                data={
                    "request_id": request_id,
                    "response": response,
                    "status": "received"
                },
                tool=f"{self.instance_type}_sampling_callback",
                message="Sampling response recorded."
            )
        
        self._tool_handlers[f"{self.instance_type}_sampling_callback"] = sampling_callback
    
    def _get_instance_documentation(self) -> Dict[str, str]:
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

**Key Documents**:
- **ASR v2.0** - Architecture Significant Record with all decisions
- **Atlas Methodology** - How to build MCP systems
- **System Design** - Architectural principles
- **Component Map** - Server relationships

Use `substrate_documentation` with `doc_type="asr-v2"` to read the complete architecture.

**How to Use Atlas**:
1. Start with me to understand the system
2. Use workflows to guide complex tasks
3. Navigate between servers using suggestions

**Example Workflow**:
1. `atlas` - Get system overview
2. `substrate_show_workflows` - Discover workflows
3. `substrate_workflow_guide` - Get step-by-step guidance
4. Follow the workflow using multiple servers

**Quick Actions**:
- Generate content: Use Synapse's stable_genius
- Format for platform: Use TLOEN's site templates
- Apply persona: Use UQBAR's personas
- Test variations: Use AKAB's experiments""",
                "examples": [
                    {
                        "description": "Get system overview",
                        "tool": "atlas",
                        "args": {}
                    },
                    {
                        "description": "Start prompt optimization workflow",
                        "tool": "substrate_workflow_guide",
                        "args": {"workflow_name": "Prompt Optimization"}
                    }
                ]
            },
            "substrate": {
                "summary": "I am the system architect providing documentation, workflows, and reference management.",
                "usage": """I am the substrate foundation. I provide:

**Documentation Access**:
- `substrate_documentation` - Read system docs (atlas, system-design, component-map)

**Workflow Navigation**:
- `substrate_show_workflows` - Discover available workflows
- `substrate_workflow_guide` - Get step-by-step guidance
- `substrate_suggest_next` - Get navigation suggestions

**Reference Management**:
- `substrate_create_ref` - Save content
- `substrate_read_ref` - Load content
- `substrate_list_refs` - Browse references

Use me to understand the system architecture and navigate between servers.""",
                "examples": [
                    {
                        "description": "Read Atlas methodology",
                        "tool": "substrate_documentation",
                        "args": {"doc_type": "atlas"}
                    },
                    {
                        "description": "Discover workflows",
                        "tool": "substrate_show_workflows",
                        "args": {}
                    }
                ]
            },
            "tloen": {
                "summary": "I transform content for specific platforms using format templates.",
                "usage": """I am TLOEN, the site format specialist. I format content for platforms like Reddit, Twitter, GitHub, etc.

**My Capabilities**:
- Transform content using platform-specific templates
- Apply formatting rules for each site
- Combine multiple platform formats

**Available Tools**:
- `tloen_execute` - Apply format templates
- `tloen_list_refs` - View available formats
- `tloen_create_ref` - Add new format templates

**Usage Pattern**:
```
tloen_execute(
    ref="sites/reddit",        # Platform template
    prompt="Your content",     # Content to format
    save_as="output/formatted" # Optional save
)
```""",
                "examples": [
                    {
                        "description": "Format for Reddit",
                        "tool": "tloen_execute",
                        "args": {
                            "ref": "sites/reddit",
                            "prompt": "My awesome project announcement"
                        }
                    },
                    {
                        "description": "Multi-platform format",
                        "tool": "tloen_execute",
                        "args": {
                            "refs": ["sites/reddit", "sites/twitter"],
                            "prompt": "Content to format"
                        }
                    }
                ],
                "available_formats": [
                    "reddit", "twitter", "github", "stackoverflow",
                    "hackernews", "linkedin", "arxiv", "wikipedia"
                ]
            },
            "uqbar": {
                "summary": "I manage writing personas and content components for consistent style.",
                "usage": """I am UQBAR, the persona and component specialist. I help you write in different voices and styles.

**My Capabilities**:
- Apply writing personas (technical, casual, creative)
- Use content components (citations, code blocks, structure)
- Combine multiple personas/components

**Available Tools**:
- `uqbar_execute` - Apply personas/components
- `uqbar_list_refs` - View available resources
- `uqbar_create_ref` - Add new personas/components

**Usage Pattern**:
```
uqbar_execute(
    ref="personas/technical_writer",  # Persona to apply
    prompt="Explain quantum computing", # Content
    save_as="output/technical"        # Optional save
)
```""",
                "examples": [
                    {
                        "description": "Apply technical persona",
                        "tool": "uqbar_execute",
                        "args": {
                            "ref": "personas/technical_writer",
                            "prompt": "Explain Docker containers"
                        }
                    },
                    {
                        "description": "Combine persona + component",
                        "tool": "uqbar_execute",
                        "args": {
                            "refs": ["personas/hemingway", "components/code_presentation"],
                            "prompt": "Tutorial on Python decorators"
                        }
                    }
                ],
                "available_personas": [
                    "technical_writer", "casual_explainer", "academic",
                    "hemingway", "shakespeare", "gordon_ramsay"
                ],
                "available_components": [
                    "code_presentation", "citation_system", "tutorial_structure"
                ]
            }
        }
        
        # Return appropriate documentation
        return docs.get(self.instance_type, {
            "summary": f"I am {self.instance_type}, part of the Atlas cognitive manipulation system.",
            "usage": self._get_instructions(),
            "examples": []
        })
    
    def _get_tools_for_instance(self) -> List[types.Tool]:
        """Get tools based on instance configuration"""
        tools = []
        
        # Base server info tool
        tools.append(types.Tool(
            name=self.instance_type,
            description=f"Get {self.instance_type} server capabilities and documentation.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ))
        
        # Sampling callback
        tools.append(types.Tool(
            name=f"{self.instance_type}_sampling_callback",
            description="Handle sampling callback responses.",
            inputSchema={
                "type": "object",
                "properties": {
                    "request_id": {"type": "string"},
                    "response": {"type": "string"}
                },
                "required": ["request_id", "response"]
            }
        ))
        
        # Add feature-specific tools based on instance type
        if self.instance_type in ["substrate", "atlas"]:
            # Documentation
            tools.append(types.Tool(
                name="substrate_documentation",
                description="Access system architecture and methodology documentation",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "doc_type": {
                            "type": "string",
                            "enum": ["overview", "atlas", "system-design", "component-map", "asr-v2"],
                            "default": "overview"
                        }
                    },
                    "required": []
                }
            ))
            
            # Workflow tools
            tools.extend([
                types.Tool(
                    name=f"{self.instance_type}_show_workflows",
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
                    name=f"{self.instance_type}_workflow_guide",
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
                    name=f"{self.instance_type}_suggest_next",
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
            ])
        
        # Reference tools (all instances have these)
        tools.extend([
            types.Tool(
                name=f"{self.instance_type}_create_ref",
                description="Create or update a reference.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "ref": {"type": "string"},
                        "content": {"type": "string"},
                        "metadata": {"type": "object"}
                    },
                    "required": ["ref", "content"]
                }
            ),
            types.Tool(
                name=f"{self.instance_type}_read_ref",
                description="Read reference content.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "ref": {"type": "string"}
                    },
                    "required": ["ref"]
                }
            ),
            types.Tool(
                name=f"{self.instance_type}_update_ref",
                description="Update existing reference.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "ref": {"type": "string"},
                        "content": {"type": "string"}
                    },
                    "required": ["ref", "content"]
                }
            ),
            types.Tool(
                name=f"{self.instance_type}_delete_ref",
                description="Delete a reference.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "ref": {"type": "string"}
                    },
                    "required": ["ref"]
                }
            ),
            types.Tool(
                name=f"{self.instance_type}_list_refs",
                description="List all references with optional prefix filter.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "prefix": {"type": "string"}
                    },
                    "required": []
                }
            )
        ])
        
        # Execute tool for TLOEN/UQBAR
        if self.instance_type in ["tloen", "uqbar"]:
            tools.append(types.Tool(
                name=f"{self.instance_type}_execute",
                description=f"Execute transformation using {self.instance_type} templates/personas",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "prompt": {"type": "string"},
                        "ref": {"type": "string"},
                        "refs": {"type": "array", "items": {"type": "string"}},
                        "prompt_ref": {"type": "string"},
                        "save_as": {"type": "string"}
                    },
                    "required": []
                }
            ))
        
        return tools
    
    def _get_instructions(self) -> str:
        """Get instance-specific instructions (backward compatibility)"""
        if self.instance_type == "tloen":
            return (
                "I am TLOEN, the site format specialist. I format content for different platforms "
                "like Reddit, StackOverflow, Twitter, etc. I use templates to transform your content "
                "into platform-specific formats.\n\n"
                "Use tloen_execute() with:\n"
                "- ref: Site format reference (e.g., 'sites/reddit')\n"
                "- prompt: Your content to format\n"
                "- save_as: Optional reference to save result"
            )
        elif self.instance_type == "uqbar":
            return (
                "I am UQBAR, the persona and module specialist. I manage writing personas, "
                "voice modules, and component composition for consistent content generation.\n\n"
                "Use uqbar_execute() with:\n"
                "- ref/refs: Persona or module references\n"
                "- prompt: Your content to transform\n"
                "- save_as: Optional reference to save result"
            )
        else:
            return (
                "I am the system architect. I tell you HOW to build (Atlas) "
                "and WHAT to build (System Design). Use me to understand the system "
                "architecture and follow the correct development methodology."
            )
    
    def register_tool(self, name: str, handler):
        """Register a tool handler"""
        self._tool_handlers[name] = handler
    
    def create_response(self, data: Any, suggestions: list = None, 
                       message: str = None, tool: str = None) -> Dict[str, Any]:
        """Create standardized response with navigation hints"""
        return self.response_builder.build(
            data=data,
            tool=tool or self._current_tool,
            suggestions=suggestions,
            message=message
        )
    
    async def run(self):
        """Run the substrate server"""
        from fastmcp.server.stdio import stdio_server
        
        try:
            logger.info(f"Starting {self.instance_type} substrate server")
            
            # Don't pass any initialization options - let the server handle it
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream=read_stream,
                    write_stream=write_stream
                )
        except Exception as e:
            logger.error(f"Server runtime error: {e}")
            raise


def create_substrate_instance():
    """Factory function to create substrate instance"""
    return SubstrateServer()


# For direct execution
if __name__ == "__main__":
    import asyncio
    
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    server = create_substrate_instance()
    asyncio.run(server.run())
