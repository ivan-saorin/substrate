"""Instance configuration module"""
from typing import Dict, List, Any
import os


def get_instance_config(instance_type: str) -> Dict[str, Any]:
    """Get configuration for a specific instance type"""
    configs = {
        "atlas": {
            "features": ["documentation", "references", "execution", "workflows"],
            "description": "Master orchestrator of the cognitive manipulation system"
        },
        "substrate": {
            "features": ["documentation", "references", "execution", "workflows"],
            "description": "Cognitive manipulation substrate"
        },
        "tloen": {
            "features": ["references", "execution"],
            "description": "Site format transformation service"
        },
        "uqbar": {
            "features": ["references", "execution"],
            "description": "Persona and component composition service"
        }
    }
    
    return configs.get(instance_type, {
        "features": ["references"],
        "description": f"{instance_type} MCP server"
    })


def should_load_feature(instance_type: str, feature_name: str) -> bool:
    """Check if a feature should be loaded for an instance"""
    config = get_instance_config(instance_type)
    return feature_name in config.get("features", [])
