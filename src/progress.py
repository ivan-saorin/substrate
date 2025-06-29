"""Progress tracking utilities to prevent MCP timeouts."""

import asyncio
import logging
import time
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


class ProgressTracker:
    """Tracks progress for long-running operations.
    
    Prevents MCP timeouts by providing regular progress updates.
    """
    
    def __init__(self, update_interval: float = 2.0):
        """Initialize progress tracker.
        
        Args:
            update_interval: Seconds between automatic progress updates
        """
        self.update_interval = update_interval
        self._active_trackers: Dict[str, "OperationTracker"] = {}
        
    def create_tracker(self, operation_name: str) -> "OperationTracker":
        """Create a new operation tracker.
        
        Args:
            operation_name: Name of the operation
            
        Returns:
            New operation tracker
        """
        tracker = OperationTracker(operation_name, self.update_interval)
        self._active_trackers[operation_name] = tracker
        return tracker
        
    def get_active_count(self) -> int:
        """Get count of active operations."""
        return len(self._active_trackers)
        
    async def cancel_all(self) -> None:
        """Cancel all active trackers."""
        for tracker in self._active_trackers.values():
            await tracker.complete()
        self._active_trackers.clear()


class OperationTracker:
    """Tracks progress for a single operation."""
    
    def __init__(self, name: str, update_interval: float):
        """Initialize operation tracker.
        
        Args:
            name: Operation name
            update_interval: Seconds between updates
        """
        self.name = name
        self.update_interval = update_interval
        self.start_time = time.time()
        self._progress = 0.0
        self._status = "Starting..."
        self._last_update = 0.0
        self._update_task: Optional[asyncio.Task] = None
        self._completed = False
        
    async def progress(self, value: float, status: str) -> None:
        """Update progress for this operation.
        
        Args:
            value: Progress value (0.0 to 1.0)
            status: Current status message
        """
        self._progress = max(0.0, min(1.0, value))
        self._status = status
        self._last_update = time.time()
        
        # Start auto-update task if not running
        if self._update_task is None and not self._completed:
            self._update_task = asyncio.create_task(self._auto_update())
            
        logger.debug(f"{self.name}: {self._progress:.0%} - {status}")
        
    async def _auto_update(self) -> None:
        """Automatically update progress to prevent timeouts."""
        try:
            while not self._completed:
                await asyncio.sleep(self.update_interval)
                
                # If no recent update, increment progress slightly
                if time.time() - self._last_update > self.update_interval:
                    # Slow incremental progress
                    increment = 0.01 * (1.0 - self._progress)
                    self._progress = min(0.99, self._progress + increment)
                    
                    elapsed = time.time() - self.start_time
                    self._status = f"Processing... ({elapsed:.1f}s)"
                    logger.debug(f"{self.name}: Auto-update {self._progress:.0%}")
                    
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Auto-update error: {e}")
            
    async def complete(self) -> None:
        """Mark operation as complete."""
        self._completed = True
        self._progress = 1.0
        self._status = "Complete"
        
        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass
                
        elapsed = time.time() - self.start_time
        logger.info(f"{self.name} completed in {elapsed:.1f}s")
        
    def get_info(self) -> Dict[str, Any]:
        """Get current progress information."""
        return {
            "name": self.name,
            "progress": self._progress,
            "status": self._status,
            "elapsed_seconds": time.time() - self.start_time,
            "completed": self._completed
        }


class ProgressContext:
    """Context manager for progress tracking.
    
    Usage:
        async with ProgressContext("my_operation") as progress:
            await progress(0.1, "Starting...")
            # ... do work ...
            await progress(0.5, "Halfway there...")
            # ... more work ...
            await progress(1.0, "Complete!")
    """
    
    def __init__(
        self,
        operation_name: str,
        tracker: Optional[ProgressTracker] = None
    ):
        """Initialize progress context.
        
        Args:
            operation_name: Name of the operation
            tracker: Optional progress tracker to use
        """
        self.operation_name = operation_name
        self.tracker = tracker or ProgressTracker()
        self._operation_tracker: Optional[OperationTracker] = None
        
    async def __aenter__(self) -> Callable:
        """Enter the context."""
        self._operation_tracker = self.tracker.create_tracker(self.operation_name)
        return self._operation_tracker.progress
        
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the context."""
        if self._operation_tracker:
            await self._operation_tracker.complete()


def estimate_progress(
    current_item: int,
    total_items: int,
    base_progress: float = 0.0,
    progress_range: float = 1.0
) -> float:
    """Estimate progress based on items processed.
    
    Args:
        current_item: Current item number (0-indexed)
        total_items: Total number of items
        base_progress: Starting progress value
        progress_range: Range of progress (default 1.0)
        
    Returns:
        Estimated progress value
    """
    if total_items <= 0:
        return base_progress
        
    item_progress = (current_item + 1) / total_items
    return base_progress + (item_progress * progress_range)
