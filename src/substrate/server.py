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

# Import shared modules
from .shared.models import get_model_registry
from .shared.prompts import PromptLoader
from .shared.response import ResponseBuilder, NavigationEngine
from .shared.storage import ReferenceManager
from .shared.instance import get_instance_config, should_load_feature

# Import features
from .features import (
    register_documentation_tools,
    register_reference_tools,
    register_execution_tools,
    register_workflow_tools
)

# Import tool schema getters
from .features.documentation.tool import get_tool_schemas as get_doc_schemas
from .features.references.tool import get_tool_schemas as get_ref_schemas
from .features.execution.tool import get_tool_schemas as get_exec_schemas
from .features.workflow_navigation.tool import get_tool_schemas as get_workflow_schemas


class SubstrateServer:
    """Base MCP server for cognitive manipulation substrate"""
    
    def __init__(self):
        self.name = "substrate"
        self.server = FastMCP(self.name)
        self.instance_type = os.getenv("INSTANCE_TYPE", "substrate")
        
        # Get instance configuration
        config = get_instance_config(self.instance_type)
        self.instance_description = config.get("description", "Cognitive manipulation substrate")
        
        logger.info(f"Initializing {self.instance_type} instance")
        
        # Core services
        self.model_registry = get_model_registry()
        self.prompt_loader = PromptLoader()
        self.response_builder = ResponseBuilder(self.instance_type)
        
        # Storage
        self.data_dir = os.getenv("DATA_DIR", "/app/data")
        self.reference_manager = ReferenceManager(self.data_dir)
        
        # Navigation engine
        self.navigation_engine = NavigationEngine()
        
        # Tool tracking
        self._current_tool = None
        self._tool_handlers = {}
        
        # Initialize
        self._register_handlers()
        self._register_tools()
        
        logger.info(f"{self.instance_type} server ready with {len(self._tool_handlers)} tools")
        
    def _register_handlers(self):
        """Register FastMCP handlers"""
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List available tools"""
            tools = []
            
            # Base tools (all instances)
            tools.append(types.Tool(
                name=self.instance_type,
                description=f"Get {self.instance_type} server capabilities and documentation.",
                inputSchema={"type": "object", "properties": {}, "required": []}
            ))
            
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
            
            # Feature-based tools
            if should_load_feature(self.instance_type, "documentation"):
                tools.extend(get_doc_schemas(self.instance_type))
            
            if should_load_feature(self.instance_type, "references"):
                tools.extend(get_ref_schemas(self.instance_type))
            
            if should_load_feature(self.instance_type, "execution"):
                tools.extend(get_exec_schemas(self.instance_type))
            
            if should_load_feature(self.instance_type, "workflows"):
                tools.extend(get_workflow_schemas(self.instance_type))
            
            return tools
            
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """Handle tool calls"""
            self._current_tool = name
            
            try:
                if name in self._tool_handlers:
                    result = await self._tool_handlers[name](**arguments)
                else:
                    result = {"error": f"Unknown tool: {name}"}
                
                import json
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                
            except Exception as e:
                logger.error(f"Error in tool {name}: {e}")
                error_result = {"error": str(e), "tool": name, "type": "execution_error"}
                return [types.TextContent(type="text", text=json.dumps(error_result, indent=2))]
            finally:
                self._current_tool = None
    
    def _register_tools(self):
        """Register all tools based on instance configuration"""
        # Base tools
        self._register_base_tools()
        
        # Feature tools
        if should_load_feature(self.instance_type, "documentation"):
            register_documentation_tools(self)
            
        if should_load_feature(self.instance_type, "references"):
            register_reference_tools(self)
            
        if should_load_feature(self.instance_type, "execution"):
            register_execution_tools(self)
            
        if should_load_feature(self.instance_type, "workflows"):
            register_workflow_tools(self)
    
    def _register_base_tools(self):
        """Register base tools (all instances have these)"""
        # Sampling callback
        async def sampling_callback(request_id: str, response: str) -> Dict[str, Any]:
            """Handle sampling responses"""
            return self.response_builder.build(
                data={"request_id": request_id, "response": response, "status": "received"},
                tool=f"{self.instance_type}_sampling_callback",
                message="Sampling response recorded."
            )
        
        self._tool_handlers[f"{self.instance_type}_sampling_callback"] = sampling_callback
    
    def register_tool(self, name: str, handler):
        """Register a tool handler"""
        self._tool_handlers[name] = handler
    
    async def run(self):
        """Run the substrate server"""
        from fastmcp.server.stdio import stdio_server
        
        try:
            logger.info(f"Starting {self.instance_type} substrate server")
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(read_stream=read_stream, write_stream=write_stream)
        except Exception as e:
            logger.error(f"Server runtime error: {e}")
            raise


def create_substrate_instance():
    """Factory function to create substrate instance"""
    return SubstrateServer()


if __name__ == "__main__":
    import asyncio
    
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    server = create_substrate_instance()
    asyncio.run(server.run())
