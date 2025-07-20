"""Reference storage management"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime


class ReferenceManager:
    """Manages reference storage for substrate instances"""
    
    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = Path(data_dir or os.getenv("DATA_DIR", "/app/data"))
        self.refs_dir = self.data_dir / "refs"
        self.refs_dir.mkdir(parents=True, exist_ok=True)
        
    async def create_ref(self, ref: str, content: str, 
                        metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create or update a reference"""
        ref_path = self._get_ref_path(ref)
        ref_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "content": content,
            "metadata": metadata or {},
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat()
        }
        
        # If exists, preserve created time
        if ref_path.exists():
            existing = await self.read_ref(ref, include_metadata=True)
            data["created"] = existing.get("created", data["created"])
        
        # Write as YAML for better readability
        ref_path.write_text(yaml.dump(data, default_flow_style=False, allow_unicode=True), encoding='utf-8')
        
        return {
            "ref": ref,
            "created": ref_path.exists(),
            "path": str(ref_path.relative_to(self.data_dir))
        }
    
    async def read_ref(self, ref: str, include_metadata: bool = False) -> Any:
        """Read reference content"""
        ref_path = self._get_ref_path(ref)
        
        if not ref_path.exists():
            raise FileNotFoundError(f"Reference not found: {ref}")
        
        # Read YAML content
        data = yaml.safe_load(ref_path.read_text(encoding='utf-8'))
        
        if include_metadata:
            return data
        return data.get("content", "")
    
    async def update_ref(self, ref: str, content: str) -> Dict[str, Any]:
        """Update existing reference"""
        # Ensure exists
        await self.read_ref(ref)
        
        # Update with new content
        return await self.create_ref(ref, content)
    
    async def delete_ref(self, ref: str) -> Dict[str, Any]:
        """Delete a reference"""
        ref_path = self._get_ref_path(ref)
        
        if not ref_path.exists():
            raise FileNotFoundError(f"Reference not found: {ref}")
        
        ref_path.unlink()
        
        # Remove empty parent directories
        try:
            ref_path.parent.rmdir()
        except OSError:
            pass  # Directory not empty
        
        return {"ref": ref, "deleted": True}
    
    async def list_refs(self, prefix: Optional[str] = None) -> List[str]:
        """List all references with optional prefix filter"""
        refs = []
        
        for ref_file in self.refs_dir.rglob("*.yaml"):
            ref = ref_file.relative_to(self.refs_dir).with_suffix('').as_posix()
            
            if prefix and not ref.startswith(prefix):
                continue
                
            refs.append(ref)
        
        return sorted(refs)
    
    def _get_ref_path(self, ref: str) -> Path:
        """Get path for reference"""
        # Sanitize ref
        ref = ref.replace('\\', '/').strip('/')
        
        # Ensure .yaml extension
        if not ref.endswith('.yaml'):
            ref = f"{ref}.yaml"
        
        return self.refs_dir / ref
