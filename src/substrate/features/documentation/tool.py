"""Documentation feature - System architecture and methodology access"""
from typing import Dict, Any, List
import os
from pathlib import Path


def register_documentation_tools(server) -> List[dict]:
    """Register documentation tools on the server"""
    
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
    
    # Register the tool handler
    server.register_tool(f"{server.instance_type}_documentation", get_documentation)
    
    return [{
        "name": f"{server.instance_type}_documentation",
        "description": "Access system architecture and methodology documentation"
    }]
