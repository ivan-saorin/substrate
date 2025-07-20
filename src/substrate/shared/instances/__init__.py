"""
Shared instances for substrate servers
Ensures single instances are used across the application
"""
import os
import logging
from ..response import ResponseBuilder, NavigationEngine
from ..models import get_model_registry
from ..prompts import PromptLoader
from ..storage import ReferenceManager

# Setup logging
logger = logging.getLogger(__name__)

# Get configuration
INSTANCE_TYPE = os.getenv("INSTANCE_TYPE", "substrate")
DATA_DIR = os.getenv("DATA_DIR", "/app/data")

# Create singleton instances
logger.info(f"Creating shared instances for {INSTANCE_TYPE}")

# Core services - created once, used everywhere
model_registry = get_model_registry()
prompt_loader = PromptLoader()
response_builder = ResponseBuilder(INSTANCE_TYPE)
navigation_engine = NavigationEngine()
reference_manager = ReferenceManager(DATA_DIR)

logger.info(f"Shared instances created for {INSTANCE_TYPE}")

# Export all instances
__all__ = [
    'model_registry',
    'prompt_loader', 
    'response_builder',
    'navigation_engine',
    'reference_manager',
    'INSTANCE_TYPE',
    'DATA_DIR'
]
