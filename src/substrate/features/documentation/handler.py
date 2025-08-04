"""
Documentation feature - Business logic handler

This handler manages documentation from multiple sources:
1. Internal YAML files in the docs/ directory (for substrate and akab)
2. External YAML files from atlas-meta (for private projects)
3. Legacy MD files support for backward compatibility
"""
import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

# Use relative imports since we're inside substrate
from ...shared.config import get_external_loader
from ...shared.instances import response_builder

logger = logging.getLogger(__name__)


class DocumentationHandler:
    """Handles documentation retrieval and management from multiple sources"""
    
    def __init__(self, instance_type: str = "substrate"):
        """Initialize documentation handler
        
        Args:
            instance_type: The instance type (substrate, atlas, tloen, etc.)
        """
        self.instance_type = instance_type
        self.response_builder = response_builder  # Use shared instance
        
        # Internal docs directory (within substrate repo)
        self.internal_docs_dir = Path(__file__).parent / "docs"
        
        # External loader for private project docs
        self.external_loader = get_external_loader()
        
        # Legacy MD docs support
        self.legacy_docs_dir = Path(os.getenv("DOCS_DIR", "/app/docs"))
        
        logger.info(f"DocumentationHandler initialized for instance: {instance_type}")
    
    async def get_documentation(self, doc_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve documentation by type
        
        Priority order:
        1. External documentation (if available)
        2. Internal YAML documentation
        3. Legacy MD documentation
        
        Args:
            doc_type: Type of documentation to retrieve. If None, uses instance_type
            
        Returns:
            Dict containing the documentation content and metadata
        """
        # Default to instance documentation if no type specified
        if doc_type is None:
            doc_type = self.instance_type
        
        try:
            # 1. Try external documentation first (for private projects)
            if self.external_loader.is_available():
                external_doc = self.external_loader.load_documentation(doc_type)
                if external_doc:
                    logger.info(f"Loaded external documentation for {doc_type}")
                    return self.response_builder.success(
                        data={
                            "content": external_doc,
                            "doc_type": doc_type,
                            "source": "external",
                            "format": "yaml"
                        },
                        message=f"Loaded external documentation for {doc_type}"
                    )
            
            # 2. Try internal YAML documentation
            internal_yaml = self.internal_docs_dir / f"{doc_type}.yaml"
            if internal_yaml.exists():
                with open(internal_yaml, 'r', encoding='utf-8') as f:
                    content = yaml.safe_load(f)
                logger.info(f"Loaded internal YAML documentation for {doc_type}")
                return self.response_builder.success(
                    data={
                        "content": content,
                        "doc_type": doc_type,
                        "source": "internal",
                        "format": "yaml"
                    },
                    message=f"Loaded internal documentation for {doc_type}"
                )
            
            # 3. Try legacy MD documentation
            legacy_md = self.legacy_docs_dir / f"{doc_type}.md"
            if legacy_md.exists():
                content = legacy_md.read_text(encoding='utf-8')
                logger.info(f"Loaded legacy MD documentation for {doc_type}")
                return self.response_builder.success(
                    data={
                        "content": content,
                        "doc_type": doc_type,
                        "source": "legacy",
                        "format": "markdown"
                    },
                    message=f"Loaded legacy documentation for {doc_type}"
                )
            
            # Documentation not found
            logger.warning(f"Documentation not found for {doc_type}")
            
            # Provide helpful message based on instance type
            if doc_type == self.instance_type:
                return self.response_builder.success(
                    data={
                        "content": self._get_default_documentation(),
                        "doc_type": doc_type,
                        "source": "generated",
                        "format": "yaml"
                    },
                    message="Default documentation generated"
                )
            else:
                # Build helpful suggestions
                suggestions = []
                
                # Suggest this instance's documentation
                suggestions.append(
                    self.response_builder.suggest_next(
                        f"{self.instance_type}_documentation",
                        f"Try '{self.instance_type}' for this instance's documentation",
                        doc_type=self.instance_type
                    )
                )
                
                # Suggest listing all docs
                suggestions.append(
                    self.response_builder.suggest_next(
                        f"{self.instance_type}_list_docs",
                        "See all available documentation"
                    )
                )
                
                # Return error with suggestions
                return self.response_builder.error(
                    error=f"Documentation type '{doc_type}' not found",
                    details={
                        "requested": doc_type,
                        "instance": self.instance_type,
                        "external_available": self.external_loader.is_available()
                    }
                )
            
        except Exception as e:
            logger.error(f"Error loading documentation {doc_type}: {e}", exc_info=True)
            return self.response_builder.error(
                error=f"Failed to load documentation: {str(e)}",
                details={
                    "doc_type": doc_type,
                    "instance": self.instance_type
                }
            )
    
    async def list_documentation(self) -> Dict[str, Any]:
        """
        List all available documentation from all sources
        
        Returns:
            Dict containing list of available documentation files
        """
        try:
            docs = []
            
            # 1. List external documentation
            if self.external_loader.is_available():
                external_types = self.external_loader.get_all_documentation_types()
                for doc_type in external_types:
                    docs.append({
                        "type": doc_type,
                        "source": "external",
                        "format": "yaml"
                    })
            
            # 2. List internal YAML documentation
            if self.internal_docs_dir.exists():
                for doc_file in self.internal_docs_dir.glob("*.yaml"):
                    doc_type = doc_file.stem
                    # Don't duplicate if already in external
                    if not any(d['type'] == doc_type and d['source'] == 'external' for d in docs):
                        docs.append({
                            "type": doc_type,
                            "source": "internal",
                            "format": "yaml",
                            "size": doc_file.stat().st_size
                        })
            
            # 3. List legacy MD documentation
            if self.legacy_docs_dir.exists():
                for doc_file in self.legacy_docs_dir.glob("*.md"):
                    doc_type = doc_file.stem
                    # Don't duplicate if already listed
                    if not any(d['type'] == doc_type for d in docs):
                        docs.append({
                            "type": doc_type,
                            "source": "legacy",
                            "format": "markdown",
                            "size": doc_file.stat().st_size
                        })
            
            logger.info(f"Found {len(docs)} documentation files")
            
            return self.response_builder.success(
                data={
                    "documentation": sorted(docs, key=lambda x: x['type']),
                    "count": len(docs),
                    "sources": {
                        "external": self.external_loader.is_available(),
                        "internal": self.internal_docs_dir.exists(),
                        "legacy": self.legacy_docs_dir.exists()
                    }
                },
                message=f"Found {len(docs)} documentation files"
            )
            
        except Exception as e:
            logger.error(f"Error listing documentation: {e}", exc_info=True)
            return self.response_builder.error(
                error=f"Failed to list documentation: {str(e)}"
            )
    
    def _get_default_documentation(self) -> Dict[str, Any]:
        """Generate default documentation for instances without specific docs"""
        return {
            "version": "1.0",
            "name": self.instance_type,
            "description": f"{self.instance_type.title()} MCP server",
            "summary": f"I am {self.instance_type.upper()}, a cognitive manipulation server.",
            "usage": f"""
I am {self.instance_type.upper()}, part of the cognitive manipulation system.

Available features depend on configuration. Use the available tools to:
- Manage references
- Execute prompts
- Access documentation

For more information, check if external documentation is available.
            """.strip()
        }
