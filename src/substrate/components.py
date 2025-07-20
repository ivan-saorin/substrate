"""Shared components for substrate-based MCP servers."""

import time
import uuid
import json
import yaml
import logging
from typing import Any, Dict, List, Optional, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class ResponseBuilder:
    """Builds standardized responses."""
    
    def create(
        self,
        success: bool = True,
        data: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None,
        error: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a standardized response - unified method."""
        response = {
            "success": success,
            "timestamp": time.time()
        }
        
        if success:
            if data is not None:
                response["data"] = data
            if message:
                response["message"] = message
        else:
            response["error"] = error or "Unknown error"
            if message:
                response["message"] = message
        
        # Add any additional fields
        response.update(kwargs)
        
        return response
    
    def success(
        self,
        data: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Build a success response."""
        return self.create(True, data, message, **kwargs)
    
    def error(
        self,
        error: str,
        error_type: str = "general",
        suggestions: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Build an error response."""
        response = self.create(False, error=error, **kwargs)
        response["error_type"] = error_type
        
        if suggestions:
            response["suggestions"] = suggestions
            
        return response
    
    def paginated(
        self,
        items: List[Any],
        page: int = 1,
        page_size: int = 10,
        total: Optional[int] = None,
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Build a paginated response."""
        data = {
            "items": items,
            "page": page,
            "page_size": page_size,
            "count": len(items)
        }
        
        if total is not None:
            data["total"] = total
            data["total_pages"] = (total + page_size - 1) // page_size
            
        return self.success(data, message)
    
    def comparison_result(
        self,
        results: List[Any],
        winner: Optional[str] = None,
        metrics: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Build a comparison result response."""
        data = {"results": results}
        
        if winner:
            data["winner"] = winner
            
        if metrics:
            data["metrics"] = metrics
            
        return self.success(data, message, **kwargs)


class ProgressTracker:
    """Tracks progress of long-running operations."""
    
    def __init__(self):
        self._operations = {}
    
    @asynccontextmanager
    async def create_context(self, operation_name: str):
        """Create a progress tracking context."""
        operation_id = str(uuid.uuid4())
        
        self._operations[operation_id] = {
            "name": operation_name,
            "progress": 0.0,
            "status": "running",
            "start_time": time.time()
        }
        
        async def update_progress(progress: float, status: str):
            """Update progress for this operation."""
            if operation_id in self._operations:
                self._operations[operation_id]["progress"] = progress
                self._operations[operation_id]["status"] = status
                logger.debug(f"{operation_name}: {progress:.0%} - {status}")
        
        try:
            yield update_progress
        finally:
            # Clean up operation
            if operation_id in self._operations:
                self._operations[operation_id]["status"] = "completed"
                self._operations[operation_id]["progress"] = 1.0


class SamplingManager:
    """Manages sampling requests and callbacks."""
    
    def __init__(self):
        self._pending_requests = {}
    
    def should_request_sampling(self, context: str) -> bool:
        """Check if we should request sampling for this context."""
        # Basic heuristic - can be overridden
        return context in ["help", "constraints", "clarification"]
    
    def create_request(
        self,
        prompt: str,
        context: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a sampling request."""
        request_id = str(uuid.uuid4())
        
        request = {
            "id": request_id,
            "prompt": prompt,
            "instruction": f"Please process and respond with request_id='{request_id}'"
        }
        
        if context:
            request["context"] = context
            
        # Store for later callback
        self._pending_requests[request_id] = {
            "prompt": prompt,
            "context": context,
            "created_at": time.time(),
            **kwargs
        }
        
        return request
    
    async def handle_callback(
        self,
        request_id: str,
        response: str
    ) -> Dict[str, Any]:
        """Handle a sampling callback."""
        if request_id not in self._pending_requests:
            logger.warning(f"Unknown sampling request: {request_id}")
            return {"processed": False, "error": "Unknown request ID"}
        
        request = self._pending_requests.pop(request_id)
        
        return {
            "processed": True,
            "original_request": request,
            "response": response,
            "processing_time": time.time() - request["created_at"]
        }
    
    async def cleanup_old_requests(self, max_age_seconds: float = 300):
        """Clean up old pending requests."""
        current_time = time.time()
        expired = []
        
        for request_id, request in self._pending_requests.items():
            if current_time - request["created_at"] > max_age_seconds:
                expired.append(request_id)
        
        for request_id in expired:
            self._pending_requests.pop(request_id)
            
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired sampling requests")


class ReferenceManager:
    """Manages reference storage and retrieval for all substrate servers.
    
    References are the core of the pipeline system:
    - Store prompts, responses, and intermediate results
    - Enable chaining between tools
    - Provide audit trail of transformations
    """
    
    def __init__(self, server_name: str, data_path: Optional[Path] = None):
        """Initialize reference manager.
        
        Args:
            server_name: Name of the server (e.g., 'synapse', 'tloen')
            data_path: Optional custom data path
        """
        self.server_name = server_name
        self.data_path = data_path or Path(f"/app/data/{server_name}")
        self.refs_path = self.data_path / "refs"
        
        # Create directories if they don't exist
        self.refs_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Reference manager initialized for {server_name} at {self.refs_path}")
    
    async def create_ref(self, ref: str, content: str, metadata: Optional[Dict] = None) -> Dict:
        """Create or update a reference.
        
        Args:
            ref: Reference name (e.g., 'pipeline/step1', 'sites/reddit')
            content: Content to store
            metadata: Optional metadata about the reference
            
        Returns:
            Dict with ref name and version
        """
        ref_path = self._get_ref_path(ref)
        ref_path.parent.mkdir(parents=True, exist_ok=True)
        
        ref_data = {
            "content": content,
            "metadata": metadata or {},
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
            "version": 1
        }
        
        # Simple versioning - increment if exists
        if ref_path.exists():
            try:
                existing = yaml.safe_load(ref_path.read_text(encoding='utf-8'))
                ref_data["version"] = existing.get("version", 0) + 1
                ref_data["created"] = existing.get("created", ref_data["created"])
            except Exception as e:
                logger.warning(f"Error reading existing ref {ref}: {e}")
        
        # Write the reference as YAML for human readability
        ref_path.write_text(yaml.dump(ref_data, default_flow_style=False, allow_unicode=True), encoding='utf-8')
        logger.debug(f"Created/updated reference: {ref} (v{ref_data['version']})")
        
        return {"ref": ref, "version": ref_data["version"]}
    
    async def read_ref(self, ref: str) -> str:
        """Read reference content.
        
        Args:
            ref: Reference name
            
        Returns:
            The content of the reference
            
        Raises:
            NotFoundError: If reference doesn't exist
        """
        ref_path = self._get_ref_path(ref)
        
        if not ref_path.exists():
            # Check for legacy .json file
            json_path = ref_path.with_suffix('.json')
            if json_path.exists():
                ref_path = json_path
            else:
                # Import here to avoid circular import
                from .errors import NotFoundError
                raise NotFoundError(f"Reference '{ref}' not found")
        
        try:
            # Try YAML first, fall back to JSON for backwards compatibility
            file_content = ref_path.read_text(encoding='utf-8')
            if ref_path.suffix == '.json':
                ref_data = json.loads(file_content)
            else:
                ref_data = yaml.safe_load(file_content)
            return ref_data["content"]
        except Exception as e:
            logger.error(f"Error reading reference {ref}: {e}")
            raise
    
    async def update_ref(self, ref: str, content: str) -> Dict:
        """Update existing reference.
        
        Just an alias for create_ref with same behavior.
        """
        return await self.create_ref(ref, content)
    
    async def delete_ref(self, ref: str) -> Dict:
        """Delete a reference.
        
        Args:
            ref: Reference name
            
        Returns:
            Dict confirming deletion
            
        Raises:
            NotFoundError: If reference doesn't exist
        """
        ref_path = self._get_ref_path(ref)
        
        if not ref_path.exists():
            from .errors import NotFoundError
            raise NotFoundError(f"Reference '{ref}' not found")
        
        ref_path.unlink()
        logger.debug(f"Deleted reference: {ref}")
        
        return {"deleted": ref}
    
    async def list_refs(self, prefix: Optional[str] = None) -> List[str]:
        """List all references with optional prefix filter.
        
        Args:
            prefix: Optional prefix to filter refs (e.g., 'pipeline/')
            
        Returns:
            Sorted list of reference names
        """
        refs = []
        
        # Look for both YAML and JSON files (for backwards compatibility)
        for pattern in ["*.yaml", "*.json"]:
            for ref_file in self.refs_path.rglob(pattern):
                # Convert path to reference name
                ref = str(ref_file.relative_to(self.refs_path).with_suffix(""))
                ref = ref.replace("\\", "/")  # Normalize path separators
                
                # Apply prefix filter if provided
                if prefix is None or ref.startswith(prefix):
                    # Avoid duplicates if both .yaml and .json exist
                    if ref not in refs:
                        refs.append(ref)
        
        return sorted(refs)
    
    async def get_ref_metadata(self, ref: str) -> Dict[str, Any]:
        """Get full reference data including metadata.
        
        Args:
            ref: Reference name
            
        Returns:
            Complete reference data
            
        Raises:
            NotFoundError: If reference doesn't exist
        """
        ref_path = self._get_ref_path(ref)
        
        if not ref_path.exists():
            # Check for legacy .json file
            json_path = ref_path.with_suffix('.json')
            if json_path.exists():
                ref_path = json_path
            else:
                from .errors import NotFoundError
                raise NotFoundError(f"Reference '{ref}' not found")
        
        try:
            file_content = ref_path.read_text(encoding='utf-8')
            if ref_path.suffix == '.json':
                return json.loads(file_content)
            else:
                return yaml.safe_load(file_content)
        except Exception as e:
            logger.error(f"Error reading reference metadata {ref}: {e}")
            raise
    
    def _get_ref_path(self, ref: str) -> Path:
        """Convert reference name to file path.
        
        Args:
            ref: Reference name
            
        Returns:
            Path to the reference file
        """
        # Normalize ref: remove leading/trailing slashes
        ref = ref.strip("/")
        
        # Convert to path: "sites/reddit" -> "refs/sites/reddit.yaml"
        return self.refs_path / f"{ref}.yaml"
    
    async def cleanup_old_refs(self, max_age_days: int = 7, prefix: str = "pipeline/"):
        """Clean up old temporary references.
        
        Args:
            max_age_days: Maximum age in days
            prefix: Prefix of refs to clean (default: pipeline temps)
            
        Returns:
            Number of refs cleaned
        """
        cleaned = 0
        cutoff_time = datetime.now().timestamp() - (max_age_days * 86400)
        
        # Clean both YAML and JSON files
        for pattern in ["*.yaml", "*.json"]:
            for ref_file in self.refs_path.glob(f"{prefix}**/{pattern}"):
                try:
                    # Check file modification time
                    if ref_file.stat().st_mtime < cutoff_time:
                        ref_file.unlink()
                        cleaned += 1
                except Exception as e:
                    logger.warning(f"Error cleaning ref {ref_file}: {e}")
        
        if cleaned > 0:
            logger.info(f"Cleaned {cleaned} old references with prefix '{prefix}'")
        
        return cleaned
