"""Reference management for Atlas system.

Handles storage and retrieval of references - reusable text snippets
that can be composed and referenced across tools.
"""

import json
import yaml
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ReferenceManager:
    """Manages references - reusable content snippets.
    
    References are stored as YAML files in a data directory.
    Each reference has:
    - Content (text)
    - Metadata (optional)
    - Creation/update timestamps
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize reference manager.
        
        Args:
            data_dir: Directory for storing references. 
                     Defaults to ./data/refs
        """
        if data_dir is None:
            # Default to data/refs relative to project root
            data_dir = Path.cwd() / "data" / "refs"
            
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Reference manager initialized with data dir: {self.data_dir}")
        
    async def create_ref(
        self, 
        ref: str, 
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create or update a reference.
        
        Args:
            ref: Reference path (e.g., 'prompts/enhanced')
            content: Reference content
            metadata: Optional metadata
            
        Returns:
            Reference info dict
        """
        ref_path = self._get_ref_path(ref)
        ref_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Prepare reference data
        ref_data = {
            'content': content,
            'metadata': metadata or {},
            'created': datetime.utcnow().isoformat(),
            'updated': datetime.utcnow().isoformat()
        }
        
        # Check if exists for update timestamp
        if ref_path.exists():
            try:
                existing = yaml.safe_load(ref_path.read_text())
                ref_data['created'] = existing.get('created', ref_data['created'])
            except Exception:
                pass  # Keep new created time
                
        # Save as YAML
        with open(ref_path, 'w', encoding='utf-8') as f:
            yaml.dump(ref_data, f, default_flow_style=False)
            
        logger.info(f"Created/updated reference: {ref}")
        
        return {
            'ref': ref,
            'path': str(ref_path),
            'created': ref_data['created'],
            'updated': ref_data['updated']
        }
        
    async def read_ref(self, ref: str) -> str:
        """Read reference content.
        
        Args:
            ref: Reference path
            
        Returns:
            Reference content
            
        Raises:
            FileNotFoundError: If reference doesn't exist
        """
        ref_path = self._get_ref_path(ref)
        
        if not ref_path.exists():
            raise FileNotFoundError(f"Reference not found: {ref}")
            
        try:
            data = yaml.safe_load(ref_path.read_text())
            return data.get('content', '')
        except Exception as e:
            logger.error(f"Error reading reference {ref}: {e}")
            raise
            
    async def update_ref(self, ref: str, content: str) -> Dict[str, Any]:
        """Update existing reference content.
        
        Args:
            ref: Reference path
            content: New content
            
        Returns:
            Reference info dict
            
        Raises:
            FileNotFoundError: If reference doesn't exist
        """
        ref_path = self._get_ref_path(ref)
        
        if not ref_path.exists():
            raise FileNotFoundError(f"Reference not found: {ref}")
            
        # Read existing data
        data = yaml.safe_load(ref_path.read_text())
        
        # Update content and timestamp
        data['content'] = content
        data['updated'] = datetime.utcnow().isoformat()
        
        # Save
        with open(ref_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False)
            
        logger.info(f"Updated reference: {ref}")
        
        return {
            'ref': ref,
            'path': str(ref_path),
            'created': data['created'],
            'updated': data['updated']
        }
        
    async def delete_ref(self, ref: str) -> bool:
        """Delete a reference.
        
        Args:
            ref: Reference path
            
        Returns:
            True if deleted, False if didn't exist
        """
        ref_path = self._get_ref_path(ref)
        
        if ref_path.exists():
            ref_path.unlink()
            logger.info(f"Deleted reference: {ref}")
            
            # Clean up empty parent directories
            try:
                ref_path.parent.rmdir()
            except OSError:
                pass  # Directory not empty
                
            return True
            
        return False
        
    async def list_refs(self, prefix: Optional[str] = None) -> List[str]:
        """List all references with optional prefix filter.
        
        Args:
            prefix: Optional prefix to filter by
            
        Returns:
            List of reference paths
        """
        refs = []
        
        # Walk the data directory
        for yaml_file in self.data_dir.rglob('*.yaml'):
            # Convert to reference path
            ref_path = yaml_file.relative_to(self.data_dir)
            ref = str(ref_path.with_suffix('')).replace('\\', '/')
            
            # Apply prefix filter if specified
            if prefix is None or ref.startswith(prefix):
                refs.append(ref)
                
        return sorted(refs)
        
    def _get_ref_path(self, ref: str) -> Path:
        """Get filesystem path for a reference.
        
        Args:
            ref: Reference path (e.g., 'prompts/enhanced')
            
        Returns:
            Path object for the reference file
        """
        # Sanitize ref path
        ref = ref.replace('..', '').strip('/')
        
        # Convert to path with .yaml extension
        ref_path = self.data_dir / ref
        if not ref_path.suffix:
            ref_path = ref_path.with_suffix('.yaml')
            
        return ref_path
        
    async def compose_input(
        self,
        prompt: Optional[str] = None,
        ref: Optional[str] = None,
        refs: Optional[List[str]] = None,
        prompt_ref: Optional[str] = None
    ) -> str:
        """Compose input from various sources.
        
        Priority: ref > refs > prompt_ref > prompt
        
        Args:
            prompt: Direct prompt text
            ref: Single reference to load
            refs: Multiple references to concatenate
            prompt_ref: Reference containing prompt
            
        Returns:
            Composed input text
            
        Raises:
            ValueError: If no input provided
        """
        # Priority order: ref > refs > prompt_ref > prompt
        if ref:
            return await self.read_ref(ref)
            
        if refs:
            # Concatenate multiple refs
            contents = []
            for r in refs:
                try:
                    content = await self.read_ref(r)
                    contents.append(content)
                except FileNotFoundError:
                    logger.warning(f"Reference not found: {r}")
                    
            if contents:
                return "\n\n---\n\n".join(contents)
                
        if prompt_ref:
            return await self.read_ref(prompt_ref)
            
        if prompt:
            return prompt
            
        raise ValueError("No input provided. Use prompt, ref, refs, or prompt_ref.")
