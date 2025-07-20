"""
Documentation feature - Business logic handler
"""
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class DocumentationHandler:
    """Handles documentation retrieval and management"""
    
    def __init__(self, docs_dir: Optional[str] = None):
        self.docs_dir = Path(docs_dir or os.getenv("DOCS_DIR", "/app/docs"))
        logger.info(f"DocumentationHandler initialized with docs_dir: {self.docs_dir}")
    
    async def get_documentation(self, doc_type: str = "overview") -> Dict[str, Any]:
        """
        Retrieve documentation by type
        
        Args:
            doc_type: Type of documentation to retrieve
            
        Returns:
            Dict containing the documentation content and metadata
        """
        doc_path = self.docs_dir / f"{doc_type}.md"
        
        try:
            if doc_path.exists():
                content = doc_path.read_text(encoding='utf-8')
                logger.info(f"Successfully loaded documentation: {doc_type}")
            else:
                # Try with .md extension if not already included
                if not doc_type.endswith('.md'):
                    alt_path = self.docs_dir / doc_type
                    if alt_path.exists():
                        content = alt_path.read_text(encoding='utf-8')
                        logger.info(f"Successfully loaded documentation: {doc_type}")
                    else:
                        content = f"Documentation type '{doc_type}' not found"
                        logger.warning(f"Documentation not found: {doc_type}")
                else:
                    content = f"Documentation type '{doc_type}' not found"
                    logger.warning(f"Documentation not found: {doc_type}")
            
            return {
                "content": content,
                "doc_type": doc_type,
                "path": str(doc_path),
                "exists": doc_path.exists()
            }
            
        except Exception as e:
            logger.error(f"Error loading documentation {doc_type}: {e}", exc_info=True)
            raise
    
    async def list_documentation(self) -> Dict[str, Any]:
        """
        List all available documentation
        
        Returns:
            Dict containing list of available documentation files
        """
        try:
            docs = []
            if self.docs_dir.exists():
                for doc_file in self.docs_dir.glob("*.md"):
                    doc_type = doc_file.stem
                    docs.append({
                        "type": doc_type,
                        "filename": doc_file.name,
                        "size": doc_file.stat().st_size
                    })
            
            logger.info(f"Found {len(docs)} documentation files")
            return {
                "documentation": docs,
                "count": len(docs),
                "docs_dir": str(self.docs_dir)
            }
            
        except Exception as e:
            logger.error(f"Error listing documentation: {e}", exc_info=True)
            raise
