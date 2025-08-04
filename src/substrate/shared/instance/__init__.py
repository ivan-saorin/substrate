"""Instance configuration module

This module provides configuration for substrate instances.
It supports both standalone operation and enhanced features
when external configurations are available.
"""
from typing import Dict, List, Any
import os

# Import the external loader - use relative import since we're in shared/instance
from ..config import get_external_loader


def get_instance_config(instance_type: str) -> Dict[str, Any]:
    """Get configuration for a specific instance type
    
    This function returns configurations for both open-source
    instances (substrate, akab) and private instances (when
    external configurations are available).
    """
    # Default public configurations that always work
    configs = {
        "substrate": {
            "features": ["documentation", "references", "execution", "workflows"],
            "description": "Cognitive manipulation substrate"
        },
        # AKAB is also open source and should work standalone
        "akab": {
            "features": ["documentation", "experiments", "comparison"],
            "description": "A/B testing and experimentation framework"
        }
    }
    
    # Try to load external configurations if available
    try:
        external_loader = get_external_loader()
        if external_loader.is_available():
            external_configs = external_loader.load_instance_configs()
            # Update with external configs (private instances)
            configs.update(external_configs)
    except Exception as e:
        # If external loading fails, continue with defaults
        # This ensures substrate and akab work standalone
        pass
    
    # Return the config for the requested instance
    return configs.get(instance_type, {
        "features": ["references"],
        "description": f"{instance_type} MCP server"
    })


def should_load_feature(instance_type: str, feature_name: str) -> bool:
    """Check if a feature should be loaded for an instance"""
    config = get_instance_config(instance_type)
    return feature_name in config.get("features", [])


def get_all_known_instances() -> List[str]:
    """Get list of all known instance types
    
    Returns both public instances and any private instances
    available through external configuration.
    """
    # Start with public instances
    instances = ["substrate", "akab"]
    
    # Add any external instances if available
    try:
        external_loader = get_external_loader()
        if external_loader.is_available():
            external_configs = external_loader.load_instance_configs()
            for instance_name in external_configs:
                if instance_name not in instances:
                    instances.append(instance_name)
    except Exception:
        # If external loading fails, just return public instances
        pass
    
    return sorted(instances)
