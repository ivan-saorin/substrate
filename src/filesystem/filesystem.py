"""
FileSystem Manager
Handles file operations for AI applications
"""
import os
import json
import shutil
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
import aiofiles
import logging

logger = logging.getLogger(__name__)


class FileSystemManager:
    """Base filesystem manager for AI applications"""
    
    def __init__(self, base_path: str = "/data"):
        self.base_path = Path(base_path)
        self._ensure_base_directory()
    
    def _ensure_base_directory(self):
        """Ensure base directory exists"""
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    async def load_json(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Load JSON file"""
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return None
        
        try:
            async with aiofiles.open(file_path, 'r') as f:
                content = await f.read()
                return json.loads(content)
        except Exception as e:
            logger.error(f"Error loading JSON from {file_path}: {e}")
            return None
    
    async def save_json(self, file_path: Path, data: Dict[str, Any]) -> bool:
        """Save data to JSON file"""
        try:
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(file_path, 'w') as f:
                await f.write(json.dumps(data, indent=2))
            logger.info(f"JSON saved: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving JSON to {file_path}: {e}")
            return False
    
    async def load_text(self, file_path: Path, encoding: str = 'utf-8') -> Optional[str]:
        """Load text file"""
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return None
        
        try:
            async with aiofiles.open(file_path, 'r', encoding=encoding) as f:
                return await f.read()
        except Exception as e:
            logger.error(f"Error loading text from {file_path}: {e}")
            return None
    
    async def save_text(
        self,
        file_path: Path,
        content: str,
        encoding: str = 'utf-8'
    ) -> bool:
        """Save text to file"""
        try:
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(file_path, 'w', encoding=encoding) as f:
                await f.write(content)
            logger.info(f"Text saved: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving text to {file_path}: {e}")
            return False
    
    async def list_files(
        self,
        directory: Path,
        pattern: str = "*",
        recursive: bool = False
    ) -> List[Path]:
        """List files in directory"""
        if not directory.exists():
            return []
        
        try:
            if recursive:
                return list(directory.rglob(pattern))
            else:
                return list(directory.glob(pattern))
        except Exception as e:
            logger.error(f"Error listing files in {directory}: {e}")
            return []
    
    async def copy_file(self, source: Path, destination: Path) -> bool:
        """Copy file to destination"""
        try:
            # Ensure destination directory exists
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Use async file operations
            async with aiofiles.open(source, 'rb') as src:
                content = await src.read()
            
            async with aiofiles.open(destination, 'wb') as dst:
                await dst.write(content)
            
            logger.info(f"File copied: {source} -> {destination}")
            return True
        except Exception as e:
            logger.error(f"Error copying {source} to {destination}: {e}")
            return False
    
    async def move_file(self, source: Path, destination: Path) -> bool:
        """Move file to destination"""
        try:
            # Ensure destination directory exists
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Use shutil for atomic move
            await asyncio.to_thread(shutil.move, str(source), str(destination))
            
            logger.info(f"File moved: {source} -> {destination}")
            return True
        except Exception as e:
            logger.error(f"Error moving {source} to {destination}: {e}")
            return False
    
    async def delete_file(self, file_path: Path) -> bool:
        """Delete file"""
        try:
            if file_path.exists():
                await asyncio.to_thread(file_path.unlink)
                logger.info(f"File deleted: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error deleting {file_path}: {e}")
            return False
    
    async def create_directory(self, directory: Path) -> bool:
        """Create directory"""
        try:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Directory created: {directory}")
            return True
        except Exception as e:
            logger.error(f"Error creating directory {directory}: {e}")
            return False
    
    async def delete_directory(self, directory: Path) -> bool:
        """Delete directory and contents"""
        try:
            if directory.exists():
                await asyncio.to_thread(shutil.rmtree, str(directory))
                logger.info(f"Directory deleted: {directory}")
            return True
        except Exception as e:
            logger.error(f"Error deleting directory {directory}: {e}")
            return False
    
    def get_file_info(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Get file information"""
        if not file_path.exists():
            return None
        
        try:
            stat = file_path.stat()
            return {
                "path": str(file_path),
                "name": file_path.name,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "is_file": file_path.is_file(),
                "is_directory": file_path.is_dir()
            }
        except Exception as e:
            logger.error(f"Error getting info for {file_path}: {e}")
            return None
    
    async def save_metadata(
        self,
        file_path: Path,
        metadata: Dict[str, Any]
    ) -> bool:
        """Save metadata for a file"""
        metadata_path = file_path.parent / f"{file_path.stem}.meta.json"
        return await self.save_json(metadata_path, metadata)
    
    async def load_metadata(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Load metadata for a file"""
        metadata_path = file_path.parent / f"{file_path.stem}.meta.json"
        return await self.load_json(metadata_path)
    
    def resolve_path(self, path: str) -> Path:
        """Resolve path relative to base_path"""
        path_obj = Path(path)
        if path_obj.is_absolute():
            return path_obj
        else:
            return self.base_path / path
