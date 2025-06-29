"""Utility functions for Substrate MCP servers."""

import asyncio
import hashlib
import json
import time
from typing import Any, Dict, List, Optional, TypeVar, Union

T = TypeVar("T")


def generate_id(prefix: str = "", length: int = 8) -> str:
    """Generate a unique ID with optional prefix.
    
    Args:
        prefix: Optional prefix for the ID
        length: Length of random part (default 8)
        
    Returns:
        Generated ID
    """
    import random
    import string
    
    chars = string.ascii_lowercase + string.digits
    random_part = "".join(random.choices(chars, k=length))
    
    if prefix:
        return f"{prefix}_{random_part}"
    return random_part


def hash_content(content: Union[str, bytes, Dict[str, Any]]) -> str:
    """Generate SHA256 hash of content.
    
    Args:
        content: Content to hash
        
    Returns:
        Hex digest of hash
    """
    if isinstance(content, dict):
        content = json.dumps(content, sort_keys=True)
    if isinstance(content, str):
        content = content.encode("utf-8")
        
    return hashlib.sha256(content).hexdigest()


def truncate_string(
    text: str,
    max_length: int = 100,
    suffix: str = "..."
) -> str:
    """Truncate string to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
        
    return text[:max_length - len(suffix)] + suffix


def format_duration(seconds: float) -> str:
    """Format duration in human-readable form.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def format_size(bytes_count: int) -> str:
    """Format byte size in human-readable form.
    
    Args:
        bytes_count: Number of bytes
        
    Returns:
        Formatted size string
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_count < 1024.0:
            return f"{bytes_count:.1f}{unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.1f}PB"


def deep_merge(
    base: Dict[str, Any],
    update: Dict[str, Any],
    merge_lists: bool = False
) -> Dict[str, Any]:
    """Deep merge two dictionaries.
    
    Args:
        base: Base dictionary
        update: Dictionary to merge in
        merge_lists: Whether to merge lists (vs replace)
        
    Returns:
        Merged dictionary
    """
    result = base.copy()
    
    for key, value in update.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value, merge_lists)
        elif key in result and merge_lists and isinstance(result[key], list) and isinstance(value, list):
            result[key] = result[key] + value
        else:
            result[key] = value
            
    return result


def sanitize_filename(filename: str, replacement: str = "_") -> str:
    """Sanitize filename for safe filesystem use.
    
    Args:
        filename: Original filename
        replacement: Character to replace invalid chars with
        
    Returns:
        Sanitized filename
    """
    import re
    
    # Remove/replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', replacement, filename)
    
    # Remove control characters
    sanitized = "".join(char for char in sanitized if ord(char) >= 32)
    
    # Trim dots and spaces
    sanitized = sanitized.strip(". ")
    
    # Ensure not empty
    if not sanitized:
        sanitized = "unnamed"
        
    return sanitized[:255]  # Max filename length


async def retry_async(
    func: Any,
    *args,
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
    **kwargs
) -> Any:
    """Retry an async function with exponential backoff.
    
    Args:
        func: Async function to retry
        *args: Function arguments
        max_attempts: Maximum retry attempts
        delay: Initial delay between retries
        backoff: Backoff multiplier
        exceptions: Exceptions to retry on
        **kwargs: Function keyword arguments
        
    Returns:
        Function result
        
    Raises:
        Last exception if all retries fail
    """
    last_error = None
    current_delay = delay
    
    for attempt in range(max_attempts):
        try:
            return await func(*args, **kwargs)
        except exceptions as e:
            last_error = e
            if attempt < max_attempts - 1:
                await asyncio.sleep(current_delay)
                current_delay *= backoff
            else:
                raise
                
    raise last_error


def chunk_list(items: List[T], chunk_size: int) -> List[List[T]]:
    """Split list into chunks of specified size.
    
    Args:
        items: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    return [
        items[i:i + chunk_size]
        for i in range(0, len(items), chunk_size)
    ]


def flatten_dict(
    data: Dict[str, Any],
    prefix: str = "",
    separator: str = "."
) -> Dict[str, Any]:
    """Flatten nested dictionary.
    
    Args:
        data: Dictionary to flatten
        prefix: Prefix for keys
        separator: Separator for nested keys
        
    Returns:
        Flattened dictionary
    """
    result = {}
    
    for key, value in data.items():
        new_key = f"{prefix}{separator}{key}" if prefix else key
        
        if isinstance(value, dict):
            result.update(flatten_dict(value, new_key, separator))
        else:
            result[new_key] = value
            
    return result


class Timer:
    """Simple timer context manager.
    
    Usage:
        with Timer() as timer:
            # ... do work ...
        print(f"Took {timer.elapsed}s")
    """
    
    def __init__(self):
        """Initialize timer."""
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        
    def __enter__(self):
        """Start timing."""
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timing."""
        self.end_time = time.time()
        
    @property
    def elapsed(self) -> float:
        """Get elapsed time in seconds."""
        if self.start_time is None:
            return 0.0
        end = self.end_time or time.time()
        return end - self.start_time
        
    @property
    def elapsed_ms(self) -> float:
        """Get elapsed time in milliseconds."""
        return self.elapsed * 1000
