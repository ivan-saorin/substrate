"""Documentation feature - System architecture and methodology access"""
from typing import Dict, Any, List
import os
import yaml
from pathlib import Path
import fastmcp.types as types


def register_documentation_tools(server) -> List[dict]:
    """Register documentation tools on the server"""
    
    # Load instance documentation once at registration time
    instance_doc = _load_instance_documentation(server.instance_type)
    
    async def get_documentation(doc_type: str = "overview") -> Dict[str, Any]:
        """Get system documentation
        
        Args:
            doc_type: Type of documentation to retrieve
                     Options: overview, atlas, system-design, component-map, asr-v2
        """
        # Try multiple locations for documentation
        possible_docs_dirs = [
            Path(__file__).parent.parent.parent.parent / "docs",  # substrate/docs
            Path(__file__).parent.parent.parent.parent.parent.parent / "docs",  # project/docs
            Path("/app/docs"),  # Docker container path
        ]
        
        doc_files = {
            "overview": "README.md",
            "atlas": "atlas.md", 
            "system-design": "system-design.md",
            "component-map": "component-map.json",
            "asr-v2": "asr-v2.md"
        }
        
        if doc_type not in doc_files:
            return server.response_builder.error(
                f"Unknown documentation type: {doc_type}",
                details={"available": list(doc_files.keys())}
            )
        
        # Find the docs directory that exists and has the files
        docs_dir = None
        doc_path = None
        
        for possible_dir in possible_docs_dirs:
            if doc_type == "overview":
                # Special case for README - check project root first
                root_readme = possible_dir.parent / "README.md"
                if root_readme.exists():
                    doc_path = root_readme
                    break
            
            test_path = possible_dir / doc_files[doc_type]
            if test_path.exists():
                docs_dir = possible_dir
                doc_path = test_path
                break
        
        if not doc_path or not doc_path.exists():
            # Try substrate/docs as fallback
            substrate_docs = Path(__file__).parent.parent.parent.parent / "docs"
            doc_path = substrate_docs / doc_files[doc_type]
            
            if not doc_path.exists():
                return server.response_builder.error(
                    f"Documentation file not found: {doc_files[doc_type]}",
                    details={
                        "searched_paths": [str(p) for p in possible_docs_dirs],
                        "file": doc_files[doc_type]
                    }
                )
        
        try:
            content = doc_path.read_text(encoding='utf-8')
            
            suggestions = []
            if doc_type == "overview":
                suggestions = [
                    server.response_builder.suggest_next(
                        f"{server.instance_type}:documentation",
                        "Read detailed Atlas methodology",
                        doc_type="atlas"
                    ),
                    server.response_builder.suggest_next(
                        f"{server.instance_type}:documentation",
                        "View Architecture Significant Record v2.0",
                        doc_type="asr-v2"
                    ),
                    server.response_builder.suggest_next(
                        f"{server.instance_type}:show_workflows",
                        "Discover available workflows"
                    )
                ]
            elif doc_type == "atlas":
                suggestions = [
                    server.response_builder.suggest_next(
                        f"{server.instance_type}:documentation", 
                        "Read system design principles",
                        doc_type="system-design"
                    ),
                    server.response_builder.suggest_next(
                        f"{server.instance_type}:documentation",
                        "View component map",
                        doc_type="component-map"
                    ),
                    server.response_builder.suggest_next(
                        f"{server.instance_type}:documentation",
                        "View Architecture Significant Record v2.0",
                        doc_type="asr-v2"
                    )
                ]
            elif doc_type == "system-design":
                suggestions = [
                    server.response_builder.suggest_next(
                        f"{server.instance_type}:documentation",
                        "View component map",
                        doc_type="component-map"
                    ),
                    server.response_builder.suggest_next(
                        f"{server.instance_type}:documentation",
                        "View Architecture Significant Record v2.0",
                        doc_type="asr-v2"
                    ),
                    server.response_builder.suggest_next(
                        f"{server.instance_type}:show_workflows",
                        "Explore available workflows"
                    )
                ]
            elif doc_type == "component-map":
                suggestions = [
                    server.response_builder.suggest_next(
                        f"{server.instance_type}:documentation",
                        "Read Atlas methodology",
                        doc_type="atlas"
                    ),
                    server.response_builder.suggest_next(
                        f"{server.instance_type}:documentation",
                        "View Architecture Significant Record v2.0",
                        doc_type="asr-v2"
                    ),
                    server.response_builder.suggest_next(
                        f"{server.instance_type}:list_refs",
                        "View stored references"
                    )
                ]
            elif doc_type == "asr-v2":
                suggestions = [
                    server.response_builder.suggest_next(
                        f"{server.instance_type}:documentation",
                        "Read Atlas methodology",
                        doc_type="atlas"
                    ),
                    server.response_builder.suggest_next(
                        f"{server.instance_type}:show_workflows",
                        "Explore implemented workflows"
                    ),
                    server.response_builder.suggest_next(
                        f"{server.instance_type}:documentation",
                        "View system design",
                        doc_type="system-design"
                    )
                ]
            
            return server.response_builder.success(
                data={
                    "doc_type": doc_type,
                    "content": content,
                    "file": doc_files[doc_type],
                    "source_path": str(doc_path)
                },
                message=f"Documentation loaded: {doc_type}",
                suggestions=suggestions
            )
            
        except Exception as e:
            return server.response_builder.error(
                f"Error reading documentation: {str(e)}",
                details={"file": doc_files[doc_type], "path": str(doc_path)}
            )
    
    async def get_server_info() -> Dict[str, Any]:
        """Get server capabilities and documentation"""
        
        # Get available tools for this instance
        tools_list = []
        for tool_name, handler in server._tool_handlers.items():
            if tool_name != server.instance_type:  # Don't include self
                tools_list.append({
                    "name": tool_name,
                    "description": handler.__doc__ or "No description"
                })
        
        # Build suggestions based on instance type
        suggestions = []
        
        if server.instance_type in ["substrate", "atlas"]:
            # Both substrate and atlas get full documentation access
            suggestions = [
                server.response_builder.suggest_next(
                    f"{server.instance_type}:documentation",
                    "Read ASR v2.0 - Complete architecture",
                    doc_type="asr-v2"
                ),
                server.response_builder.suggest_next(
                    f"{server.instance_type}:documentation",
                    "Read Atlas methodology",
                    doc_type="atlas"
                ),
                server.response_builder.suggest_next(
                    f"{server.instance_type}:show_workflows",
                    "Discover available workflows"
                )
            ]
        elif server.instance_type == "tloen":
            suggestions = [
                server.response_builder.suggest_next(
                    "tloen:list_refs",
                    "View available site formats",
                    prefix="sites"
                ),
                server.response_builder.suggest_next(
                    "tloen:execute",
                    "Format content for a platform"
                )
            ]
        elif server.instance_type == "uqbar":
            suggestions = [
                server.response_builder.suggest_next(
                    "uqbar:list_refs",
                    "View available personas",
                    prefix="personas"
                ),
                server.response_builder.suggest_next(
                    "uqbar:list_refs",
                    "View available components",
                    prefix="components"
                )
            ]
        
        return server.response_builder.build(
            data={
                "name": server.instance_type,
                "version": "2.0.0",
                "description": server.instance_description,
                "documentation": instance_doc,
                "tools": tools_list,
                "tool_count": len(server._tool_handlers),
                "model_registry": {
                    "providers": list(set(m.provider.value for m in server.model_registry.models.values())),
                    "models": len(server.model_registry.models)
                }
            },
            tool=server.instance_type,
            message=f"{server.instance_type.upper()} server ready. {instance_doc.get('summary', '')}",
            suggestions=suggestions
        )
    
    # Register the tool handlers
    if server.instance_type in ["substrate", "atlas"]:
        server.register_tool(f"{server.instance_type}_documentation", get_documentation)
    
    server.register_tool(server.instance_type, get_server_info)
    
    # Tool schemas for FastMCP
    tool_schemas = []
    
    # Only substrate and atlas get the documentation tool
    if server.instance_type in ["substrate", "atlas"]:
        tool_schemas.append({
            "name": f"{server.instance_type}_documentation",
            "description": "Access system architecture and methodology documentation"
        })
    
    return tool_schemas


def _load_instance_documentation(instance_type: str) -> Dict[str, Any]:
    """Load instance-specific documentation from YAML files"""
    doc_path = Path(__file__).parent / "docs" / f"{instance_type}.yaml"
    
    if not doc_path.exists():
        # Return minimal documentation if file doesn't exist
        return {
            "summary": f"I am {instance_type}, part of the Atlas cognitive manipulation system.",
            "usage": f"Use {instance_type} tools to access this server's capabilities.",
            "examples": []
        }
    
    try:
        with open(doc_path, 'r', encoding='utf-8') as f:
            doc_data = yaml.safe_load(f)
        
        return {
            "summary": doc_data.get("summary", ""),
            "usage": doc_data.get("usage", ""),
            "examples": doc_data.get("examples", [])
        }
    except Exception as e:
        return {
            "summary": f"I am {instance_type}, part of the Atlas cognitive manipulation system.",
            "usage": f"Error loading documentation: {str(e)}",
            "examples": []
        }


def get_tool_schemas(instance_type: str) -> List[types.Tool]:
    """Get FastMCP tool schemas for documentation tools"""
    tools = []
    
    # Only substrate and atlas get documentation tool
    if instance_type in ["substrate", "atlas"]:
        tools.append(types.Tool(
            name=f"{instance_type}_documentation",
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
    
    return tools
